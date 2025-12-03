# app/retrieval.py
import json
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parents[1]
CUSTOMERS_PATH = BASE / "data" / "customers.json"
STORES_PATH = BASE / "data" / "stores.json"

def get_customer_by_masked_token(token: str) -> Optional[dict]:
    """
    token is the user_token provided by client, e.g. "<EMAIL_1>".
    This function maps token -> customer record from data/customers.json.
    """
    if not token:
        return None
    if not CUSTOMERS_PATH.exists():
        return None
    with open(CUSTOMERS_PATH, "r", encoding="utf8") as fh:
        customers = json.load(fh)
    # customers: list of { "id": "...", "token": "<EMAIL_1>", "name": "...", ...}
    for c in customers:
        if c.get("token") == token:
            return c
    return None

def find_nearest_store() -> dict:
    """
    Return a mocked nearest store info. In real implementation compute haversine.
    """
    if not STORES_PATH.exists():
        return {"name":"StarBrew (demo)", "distance_m":50, "inventory":["Hot Chocolate","Latte","Iced Latte"], "offers":["HOT10","WINTER5"]}
    with open(STORES_PATH, "r", encoding="utf8") as fh:
        stores = json.load(fh)
    # return the first store for demo
    return stores[0] if stores else {"name":"StarBrew (demo)", "distance_m":50, "inventory":["Hot Chocolate"], "offers":["HOT10"]}
