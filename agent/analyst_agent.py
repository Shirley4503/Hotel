import os
import streamlit as st
from openai import OpenAI


def get_openai_client():
    api_key = None

    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def analyze_result(user_question: str, sql: str, result_markdown: str, rag_context: str = "") -> str:
    """
    Explain query results in hotel operations language.
    """
    client = get_openai_client()
    if client is None:
        return "OPENAI_API_KEY is missing, so I can show the SQL result but cannot generate an AI analysis yet."

    prompt = f"""
You are HotelMind, a hotel operations analyst.

User question:
{user_question}

SQL used:
{sql}

Query result:
{result_markdown}

Relevant hotel context:
{rag_context}

Write a concise manager-friendly answer.

Include:
1. Direct answer
2. Key operational insight
3. Suggested action if relevant

Rules:
- Do not invent numbers not shown in the result.
- If the result is empty, say no matching records were found.
- Keep the tone professional and clear.
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "You explain hotel database query results accurately and concisely."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
