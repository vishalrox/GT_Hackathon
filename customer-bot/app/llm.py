# app/llm.py
import os
from typing import Optional
import openai
import time

DEFAULT_MODEL = "gpt-4o-mini"  # change if you prefer another model

def generate_reply(prompt: str, openai_api_key: Optional[str] = None, model: str = DEFAULT_MODEL, max_tokens: int = 256) -> str:
    """
    If openai_api_key provided, calls OpenAI ChatCompletion.
    Otherwise returns a deterministic fallback string.
    IMPORTANT: prompt must contain only masked PII tokens.
    """
    if not openai_api_key:
        # fallback deterministic reply for offline demos
        snippet = prompt[:400].replace("\n", " ")
        return f"[LLM offline demo] Based on your message (masked): {snippet}... (enable OPENAI_API_KEY to use a real model)"

    openai.api_key = openai_api_key
    for attempt in range(3):
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an assistant for an in-store retail chain. Be concise and actionable. Use available snippets and customer preferences to personalize replies. Never ask for PII."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            text = completion.choices[0].message.content.strip()
            return text
        except Exception as e:
            wait = 1 + attempt * 2
            time.sleep(wait)
            last_err = e
    return f"[LLM error] {last_err}"
