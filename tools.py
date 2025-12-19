def get_order_status(order_id: str) -> dict:
    """Mock tool: replace with real DB/API later."""
    mock = {
        "A1001": {"status": "Shipped", "carrier": "DHL", "eta": "2-3 days"},
        "A1002": {"status": "Processing", "carrier": None, "eta": "3-5 days"},
        "A1003": {"status": "Delivered", "carrier": "FedEx", "eta": "Delivered yesterday"},
    }
    return mock.get(order_id, {"status": "Not found", "carrier": None, "eta": None})