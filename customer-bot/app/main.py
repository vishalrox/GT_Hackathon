# app/main.py
import os
from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.masking import mask_pii, unmask_safe
from app import rag, llm, retrieval
import typing

app = FastAPI(title="Customer Experience Automation - RAG+LLM MVP")

@app.get("/", tags=["health"])
def root():
    return {"status":"ok","message":"Customer-bot running. Open /docs to use the API UI."}

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def build_prompt(masked_user_text: str, customer: typing.Optional[dict], store: dict, doc_snippets: list) -> str:
    customer_text = ""
    if customer:
        prefs = ", ".join(customer.get("preferences", []))
        hist = customer.get("history", [])
        hist_text = "; ".join([f"{h.get('item')} x{h.get('count',1)} (last:{h.get('last_order','-')})" for h in hist])
        customer_text = f"Customer name: {customer.get('name')}. Preferences: {prefs}. History: {hist_text}."

    docs_text = "\n\n".join([f"Source: {m.get('source')} — {t[:400]}" for t,m,score in doc_snippets])

    prompt = (
        "You are a helpful assistant for a retail coffee chain. Respond concisely with a clear action or suggestion.\n\n"
        f"Customer message (PII masked): {masked_user_text}\n\n"
        f"{customer_text}\n"
        f"Nearest store: {store.get('name')} (distance_m={store.get('distance_m')}). Inventory: {', '.join(store.get('inventory',[]))}. Offers: {', '.join(store.get('offers',[]))}\n\n"
        "Relevant documents:\n" + (docs_text or "None") + "\n\n"
        "Write one concise reply the agent can send. If a coupon is available and relevant, mention it. If the customer is cold, suggest a hot drink and offer to reserve it."
    )
    return prompt

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 1) mask incoming text
    masked_text, mapping = mask_pii(req.user_text)

    # 2) fetch customer record by token
    customer = None
    if req.user_token:
        customer = retrieval.get_customer_by_masked_token(req.user_token)

    # 3) nearest store
    store = retrieval.find_nearest_store()

    # 4) build retrieval query (safe masked_text)
    retrieval_query = masked_text
    if customer:
        retrieval_query += " " + " ".join(customer.get("preferences", [])[:3])

    # 5) query RAG (filter by customer.id if present)
    customer_id = customer.get("id") if customer else None
    try:
        top_docs_raw = rag.query(retrieval_query, k=3, customer_id=customer_id)
    except Exception:
        top_docs_raw = []

    # adapt format for prompt: each item is (text, metadata, score)
    doc_snippets = [(t, m, s) for t,m,s in top_docs_raw]

    # 6) build prompt (masked)
    prompt = build_prompt(masked_text, customer, store, doc_snippets)

    # 7) generate reply (OpenAI if key present else fallback)
    reply_from_llm = llm.generate_reply(prompt, openai_api_key=OPENAI_KEY)

    # 8) unmask safely for display (partial masks)
    final_reply = unmask_safe(reply_from_llm, mapping)
    return ChatResponse(reply=final_reply)
