import os
import json
import requests

from tools import get_order_status


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def velocity_chat(messages):
    api_key = os.getenv("VELOCITY_API_KEY", "").strip()
    base_url = os.getenv("VELOCITY_BASE_URL", "https://chat.velocity.online/api").strip()
    model = os.getenv("VELOCITY_MODEL", "gpt-5.2").strip()
    temperature = float(os.getenv("VELOCITY_TEMPERATURE", "0.2"))
    timeout = int(os.getenv("VELOCITY_TIMEOUT", "60"))

    if not api_key:
        raise RuntimeError("Missing VELOCITY_API_KEY in .env")

    # If VELOCITY_ENDPOINT is set, try it first, then fall back to common ones.
    preferred = os.getenv("VELOCITY_ENDPOINT", "").strip()

    candidate_endpoints = []
    if preferred:
        candidate_endpoints.append(preferred)

    # Common OpenAI-compatible routes
    candidate_endpoints += [
        "/v1/chat/completions",
        "/api/v1/chat/completions",
        "/v1/completions",
        "/api/v1/completions",
        "/chat/completions",
        "/api/chat/completions",
    ]

    # Auth header variants (different providers use different styles)
    header_variants = [
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"x-api-key": api_key, "Content-Type": "application/json"},
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    last_error = None

    for ep in candidate_endpoints:
        url = base_url.rstrip("/") + "/" + ep.lstrip("/")

        for headers in header_variants:
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=timeout)
                if r.status_code >= 400:
                    last_error = f"HTTP {r.status_code} at {url}: {r.text}"
                    continue

                data = r.json()
                # Chat-completions style
                msg = data["choices"][0]["message"]
                # Print once so you know what worked
                # (comment out later if you want)
                print(f"[OK] Using endpoint: {ep} | auth: {'Authorization' if 'Authorization' in headers else 'x-api-key'}")
                return msg

            except Exception as e:
                last_error = f"Exception at {url}: {e}"
                continue

    raise RuntimeError("All endpoint/auth attempts failed.\nLast error:\n" + str(last_error))


def try_parse_tool_call(text: str):
    """
    Very simple tool call protocol:
    If model outputs a single line JSON like:
      {"tool":"get_order_status","order_id":"A1001"}
    we'll run the tool.
    """
    text = text.strip()
    if not (text.startswith("{") and text.endswith("}")):
        return None
    try:
        obj = json.loads(text)
    except Exception:
        return None

    if obj.get("tool") == "get_order_status" and "order_id" in obj:
        return obj
    return None


def run():
    system_prompt = read_text("prompt.txt")
    products = read_json("products.json")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": "PRODUCT CATALOG:\n" + json.dumps(products, indent=2)},
        {
            "role": "system",
            "content": (
                "TOOL INSTRUCTIONS:\n"
                "If you need order status, respond ONLY with JSON exactly in this format:\n"
                '{"tool":"get_order_status","order_id":"A1001"}\n'
                "Otherwise, respond normally to the user."
            ),
        },
    ]

    print("first_agent (Velocity) - with products.json + tool")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Bye.")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # 1) Ask model
        assistant_msg = velocity_chat(messages)
        content = (assistant_msg.get("content") or "").strip()

        # 2) If it asked to call tool, run it and ask model again with tool result
        tool_req = try_parse_tool_call(content)
        if tool_req:
            order_id = tool_req["order_id"]
            tool_result = get_order_status(order_id)

            messages.append({"role": "assistant", "content": content})
            messages.append(
                {
                    "role": "system",
                    "content": f"TOOL_RESULT get_order_status({order_id}) => {json.dumps(tool_result)}",
                }
            )

            assistant_msg2 = velocity_chat(messages)
            content2 = (assistant_msg2.get("content") or "").strip()

            messages.append({"role": "assistant", "content": content2})
            print("\nBot:", content2, "\n")
        else:
            messages.append({"role": "assistant", "content": content})
            print("\nBot:", content, "\n")


if __name__ == "__main__":
    load_env()
    run()