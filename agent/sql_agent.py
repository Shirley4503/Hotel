import os
import streamlit as st
from openai import OpenAI
from tools.schema_tool import get_database_schema


def get_openai_client():
    """
    Works both locally and on Streamlit Cloud.
    On Streamlit Cloud, set OPENAI_API_KEY in App Settings -> Secrets.
    """
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


def generate_sql(user_question: str, rag_context: str = "") -> str:
    """
    Generate a SQLite SELECT query using schema + retrieved business context.
    """
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to Streamlit Secrets.")

    schema = get_database_schema()

    prompt = f"""
You are a SQL generation agent for a hotel operations database.

Your task:
Write ONE SQLite-compatible SELECT query that answers the user's question.

Hard rules:
- Output SQL only.
- Use only SELECT.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, TRUNCATE, PRAGMA, VACUUM.
- Use only tables and columns from the database schema.
- Do not invent table names or column names.
- Prefer clear aliases and readable column names.
- Use LIMIT 50 unless the user asks for a full summary or aggregate.
- If the question asks for revenue, use charge.amount and join service when service type is needed.
- If the question asks for available rooms, use room and room_reservation.
- If the question asks for access logs, use card_access_log, access_card, person, and room.
- If the question asks for billing responsibility, use billing_party, charge, person, organization, and service.
- If the question asks for events, use event, event_room, room, host, and person.
- If the question asks for room details, join room, floor, wing, building, sleeping_room_details, meeting_room_details when needed.

Database schema:
{schema}

Retrieved hotel business context:
{rag_context}

User question:
{user_question}

Return SQL only:
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "You generate safe SQLite SELECT queries for a hotel operations database."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql
