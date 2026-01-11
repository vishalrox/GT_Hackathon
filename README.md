Customer Experience Automation – The Hyper-Personalized Retail Assistant

Tagline: An AI-powered, privacy-safe customer assistant that turns raw customer data + PDFs into instant, personalized responses using RAG, masking, and LLMs.

1. The Problem (Real-World Scenario)

Customers today expect instant, context-aware answers:

“Is Hot Chocolate available right now?”

“Do I have coupons left?”

“Which store is nearest to me?”

But most chatbots are generic, unable to understand customer history, behavior, or store inventory.
Worse, customer data (emails, phone numbers, invoices) is sensitive, and sending raw PII to LLMs is unsafe.

The Pain Point

Retail support agents manually check:

Customer purchase history

Offers/coupons

Store availability

PDFs containing customer policies

This slows response time and leads to inconsistent customer experiences.

My Solution

I built Customer Experience Automation, a fully automated system that:

Understands customer context

Reads customer-specific PDFs using RAG

Suggests personalized offers

Masks PII so nothing sensitive ever reaches the LLM

Generates a natural, helpful reply — instantly

Result: an AI agent that feels like a real in-store assistant.

2. Expected End Result
User Experience

Input:
Customer messages the bot:

“I’m cold and outside. My phone is +91-98765-43210.”

System Automatically:

Masks PII → <PHONE_1>, <EMAIL_1>

Finds correct customer profile

Retrieves only that customer’s PDFs (policy/invoice)

Fetches nearest store + live offers

Builds a smart LLM prompt

Generates a personalized response

Output:
A super-personal reply like:

“You’re just 50m from StarBrew Main Street. Since you're cold and love Hot Chocolate, I can get one ready for you.
You also have a HOT10 discount. Want me to apply it?”

3. Technical Approach

Built as a production-ready AI system, not a basic script.

System Architecture Overview

User Message
     │
     ▼
[1] PII Masking Engine (Regex-based)
     │
     ▼
[2] RAG Retriever (FAISS + SentenceTransformers)
     │
     ▼
[3] Customer Intelligence (preferences + history)
     │
     ▼
[4] Store Intelligence (inventory + offers)
     │
     ▼
[5] LLM Prompt Constructor
     │
     ▼
[6] OpenAI LLM (masked input only)
     │
     ▼
[7] Safe Partial Unmasking
     │
     ▼
Final Personalized Reply

Key Design Choices
1. Privacy First (Hackathon Requirement)

Raw PII is removed before indexing PDFs

Raw PII is removed before calling LLM

Only safe, partial unmasking is shown to user

Zero chance of LLM leakage

2. RAG for Customer Personalization

Every customer has PDFs: invoice, notes, policy

Indexed with SentenceTransformers

Stored in FAISS vector DB

Retrieval filtered by customer_id

3. FastAPI Backend

Clean /chat API endpoint

Swagger UI for interactive testing

Modular code structure (masking, rag, utils)

4. Offline-Safe Fallback

If no OpenAI API key is provided → deterministic replies.

4. Tech Stack

~~~

| Layer                    | Tools Used                    |
| ------------------------ | ----------------------------- |
| **Backend Framework**    | FastAPI                       |
| **Vector Search Engine** | FAISS                         |
| **Embeddings**           | SentenceTransformers          |
| **PDF Extraction**       | PyPDF                         |
| **Data Privacy**         | Custom PII Masking Engine     |
| **LLM**                  | OpenAI GPT-4o-mini (optional) |
| **Orchestration**        | Python 3.11                   |
| **Storage**              | JSON + File-based FAISS index |

~~~

5. Challenges & Learnings
   
⚠️ Challenge 1: PII Leakage Prevention

Problem: Customer PDFs contain phones & emails — unsafe to send to an LLM.

Solution:
I built a two-stage masking layer:

Mask PDFs before indexing

Mask user inputs dynamically

This ensured absolute privacy compliance.

⚠️ Challenge 2: Customer-Specific RAG Retrieval

By default RAG returns the closest chunks — even if they belong to a different customer.

Solution:
Add metadata filtering in the FAISS post-processing:

if customer_id and md.get("customer_id") != customer_id:
    continue

Now each customer only retrieves their own documents.

⚠️ Challenge 3: Making Replies Truly Personalized

Merged:

Customer preferences

Purchase history

Store inventory

Active coupons

RAG PDF content

This created deeply personalized outputs.

6. Output Example

Here is a real output (also saved as PDF in output/output.pdf):

“You’re just 50m from StarBrew Main Street.
Since you’re cold and enjoy Hot Chocolate, shall I prepare one?
You're eligible for the HOT10 coupon.”

PDF available at:
output/output.pdf

7. Repository Structure
~~~
customer-bot/
│
├── app/
│   ├── main.py
│   ├── rag.py
│   ├── masking.py
│   ├── pdf_utils.py
│   ├── llm.py
│   ├── retrieval.py
│   └── schemas.py
│
├── data/
│   ├── customers.json
│   ├── stores.json
│   └── docs/
│        ├── cust_cust_001_policy.pdf
│        ├── cust_cust_001_invoice.pdf
│        ├── cust_cust_002_notes.pdf
│        └── store_info.txt
│
├── output/
│   └── final_output.pdf
│
├── requirements.txt
└── README.md
~~~

8. How to Run
1. Install dependencies
pip install -r requirements.txt

2. Build PDF RAG Index
python3 -m app.rag build

3. Start server
uvicorn app.main:app --reload --port 8000

4. Test with curl
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_text":"I am cold and outside.","user_token":"<EMAIL_1>"}'

9. Future Enhancements

Weather-based personalization

Geo-based nearest store detection

WhatsApp/Twilio chatbot

React-based UI

Multi-store inventory APIs

Voice support (TTS + STT)

✨ Final Thoughts

This project demonstrates how privacy-safe AI + RAG transforms customer interaction.
It blends real-world retail logic with modern AI workflows, making it powerful, fast, and practical.
