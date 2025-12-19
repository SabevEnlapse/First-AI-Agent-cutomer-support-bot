🧠 NovaTech AI Agent (Velocity / Tool-Calling)

A production-style AI customer support agent built in Python.
The agent can:

Answer questions using a product catalog (JSON)

Decide when to call tools (functions) on its own

Retrieve order status via a backend function

Run locally with environment-based configuration

Integrate with Velocity-hosted GPT models (UI-backed access)

📂 Project Structure
first_agent/
│
├── agent.py          # Main agent loop (reason → act → observe)
├── tools.py          # Tool implementations (order status, etc.)
├── products.json     # Product catalog (knowledge base)
├── prompt.txt        # System prompt (agent rules & behavior)
├── .env              # Environment variables (API config)
└── README.md

⚙️ Requirements

Python 3.10+

pip installed

Internet access (for Velocity UI models)

Python dependencies
pip install requests

🔐 Environment Configuration

Create a .env file in the project root:

VELOCITY_API_KEY=your_api_key_here
VELOCITY_BASE_URL=https://chat.velocity.online/api
VELOCITY_MODEL=gpt-5.1
VELOCITY_TEMPERATURE=0.2
VELOCITY_TIMEOUT=60


⚠️ Never commit .env to git
API keys must remain private.

🧠 How the Agent Works (High Level)

The agent follows a classic agent loop:

User input

LLM reasoning

Optional tool call

Tool execution

Final response

Decision protocol

The model is instructed to either:

Respond directly OR

Output JSON requesting a tool call

Example tool request:

{"tool":"get_order_status","order_id":"ORD-1001"}

🛠️ Tools
get_order_status(order_id)

Defined in tools.py.

Returns structured data such as:

{
  "order_id": "ORD-1001",
  "status": "shipped",
  "carrier": "DHL",
  "estimated_delivery": "2 days"
}


The agent cannot fabricate order data — it must use the tool.

📚 Product Knowledge

The agent uses products.json as its only source of product truth.

No hallucinated products

No invented prices

No unauthorized changes

Example questions:

“What products do you sell?”

“Tell me about the NovaTech X1 laptop”

“Which product is the cheapest?”

▶️ Running the Agent

From the project directory:

python agent.py


You should see:

first_agent (Velocity) - with products.json + tool
Type 'exit' to quit.

🧪 Test Scenarios
Product questions
What products do you sell?
Tell me about the NovaTech X1
Which product is best for students?

Tool usage
Where is my order?


Then provide:

ORD-1001

Edge cases
Do you sell phones?
What's the weather today?
Give me a discount


The agent should politely refuse unsupported requests.

🚨 Important Notes About Velocity

chat.velocity.online is UI-first, not a public OpenAI-compatible API

Browser URLs (/?model=...) are NOT API endpoints

Programmatic access depends on internal/company configuration

This project assumes authorized internal usage

If an official backend endpoint is provided, the agent can be adapted instantly.

🔒 Security & Safety

No API keys in code

No filesystem writes

Read-only product catalog

Tool calls are strictly validated

JSON parsing is defensive

🧩 Extending the Agent

Possible upgrades:

Multiple tools

Persistent memory (vector DB)

Streaming responses

Logging & observability

Web UI / API wrapper

Tool schema validation

🏁 Summary

This project demonstrates:

✅ A real agent, not a chatbot

✅ Tool-calling with reasoning

✅ External knowledge grounding

✅ Production-style structure

✅ Clean separation of concerns

If you can run this and explain it —
you understand AI agents at a professional level.
