# HotelMind: Multi-Agent Hotel Operations Assistant
A Streamlit-based AI agent that lets hotel staff ask natural-language questions about rooms, reservations, events, billing, reports, and access logs, then automatically queries the hotel database and returns operational insights.

User Question

↓

ChromaDB RAG Skill

从 knowledge_base 里检索相关 schema / business rules / KPI / anomaly rules

↓

SQL Agent

LLM 根据用户问题 + ChromaDB context + database schema 生成 SQLite SELECT query

↓

QC Agent

检查 SQL 是否安全，只允许 SELECT，不允许 UPDATE/DELETE/DROP

↓

Database Tool

执行 SQL，查询 hotel.db

↓

Analyst Agent

把查询结果解释成 hotel manager 能看懂的运营分析

↓

Final Answer
