import os
import streamlit as st
import pandas as pd

from skills.sql_generation_skill import answer_with_generated_sql
from skills.fixed_report_skill import (
    get_summary_stats,
    revenue_by_service,
    room_status_summary,
    recent_access_logs,
)
from tools.schema_tool import get_database_schema
from skills.chroma_rag_skill import retrieve_context_chroma
from data.build_chroma import build_chroma


st.set_page_config(
    page_title="HotelMind AI",
    page_icon="🏨",
    layout="wide",
)


# -----------------------------
# Helper functions
# -----------------------------

def has_openai_key() -> bool:
    """
    Check whether OpenAI API key exists either in Streamlit Secrets or environment variables.
    """
    try:
        if st.secrets.get("OPENAI_API_KEY"):
            return True
    except Exception:
        pass

    return bool(os.getenv("OPENAI_API_KEY"))


def show_project_intro():
    st.markdown(
        """
        **HotelMind AI** is a ChromaDB-RAG and LLM-generated SQL agent for hotel operations.

        It can:
        - retrieve relevant hotel schema and business rules from ChromaDB;
        - generate safe SQLite `SELECT` queries with an LLM;
        - query `hotel.db`;
        - explain results as a hotel operations analyst;
        - show dashboard insights even without the OpenAI API key.
        """
    )


def show_api_key_warning():
    if not has_openai_key():
        st.warning(
            """
            OpenAI API key is not detected.  
            The Dashboard and ChromaDB build features can still run, but the LLM SQL Agent will not work yet.

            On Streamlit Cloud, add this under **App settings → Secrets**:

            ```toml
            OPENAI_API_KEY = "your_real_key_here"
            OPENAI_MODEL = "gpt-4o-mini"
            ```
            """
        )


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("🏨 HotelMind AI")

st.sidebar.markdown(
    """
    **Agent Architecture**
    
    1. ChromaDB RAG Skill  
    2. LLM SQL Generation Skill  
    3. SQL Safety QC Skill  
    4. SQLite Database Query Tool  
    5. Hotel Operations Analyst Agent  
    """
)

st.sidebar.divider()

st.sidebar.markdown("### Setup Checklist")
st.sidebar.markdown(
    """
    - `hotel.db` uploaded  
    - `knowledge_base/*.md` added  
    - `requirements.txt` includes `chromadb`  
    - ChromaDB built  
    - OpenAI key added in Streamlit Secrets  
    """
)

st.sidebar.divider()

if has_openai_key():
    st.sidebar.success("OpenAI API key detected")
else:
    st.sidebar.warning("OpenAI API key not detected")


# -----------------------------
# Main page
# -----------------------------

st.title("🏨 HotelMind AI")
st.caption("ChromaDB RAG + LLM-generated SQL + Skills for Hotel Operations Intelligence")

show_project_intro()
show_api_key_warning()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Ask HotelMind",
        "Dashboard",
        "Build / Test ChromaDB",
        "Database Schema",
        "About Skills",
    ]
)


# -----------------------------
# Tab 1: Ask HotelMind
# -----------------------------

with tab1:
    st.subheader("Ask HotelMind")

    st.markdown(
        """
        Ask a natural-language question about the hotel database.  
        HotelMind will retrieve relevant rules from ChromaDB, generate SQL, check SQL safety, query `hotel.db`, and explain the result.
        """
    )

    example_questions = [
        "Which service types generate the most revenue?",
        "Show the top 10 rooms by total revenue.",
        "Which rooms are currently available?",
        "Show recent card access logs.",
        "Which billing parties have the highest total charges?",
        "Show event room usage by date.",
        "Find guests with multiple stays.",
        "Show room status breakdown.",
        "Which events have the highest estimated attendance?",
        "Show charges related to events.",
        "Which rooms are near the pool?",
        "Show guests and their stay history.",
    ]

    selected_example = st.selectbox(
        "Try an example question",
        [""] + example_questions,
    )

    user_question = st.text_area(
        "Your question",
        value=selected_example,
        placeholder="Example: Which service types generate the most revenue?",
        height=110,
    )

    run_agent = st.button("Run HotelMind Agent", type="primary")

    if run_agent:
        if not user_question.strip():
            st.error("Please enter a question first.")
        elif not has_openai_key():
            st.error(
                "OpenAI API key is missing. Add it in Streamlit Cloud Secrets before running the LLM SQL Agent."
            )
        else:
            with st.spinner(
                "HotelMind is retrieving ChromaDB context, generating SQL, checking safety, and querying hotel.db..."
            ):
                result = answer_with_generated_sql(user_question.strip())

            st.markdown("### 1. Generated SQL")
            if result.get("sql"):
                st.code(result["sql"], language="sql")
            else:
                st.info("No SQL was generated.")

            st.markdown("### 2. SQL Safety QC")
            if result.get("success"):
                st.success(result.get("qc_message", "SQL passed safety check."))
            else:
                st.error(result.get("qc_message", "SQL did not pass safety check."))

            st.markdown("### 3. Query Result")
            df = result.get("dataframe")
            if df is not None:
                st.dataframe(df, use_container_width=True)

                if isinstance(df, pd.DataFrame) and not df.empty:
                    st.caption(f"Returned {len(df)} row(s).")
                else:
                    st.info("The query returned no rows.")
            else:
                st.warning("No dataframe to display.")

            st.markdown("### 4. HotelMind Analysis")
            st.write(result.get("analysis", "No analysis generated."))

            with st.expander("Retrieved ChromaDB RAG Context"):
                rag_context = result.get("rag_context", "")
                if rag_context:
                    st.text(rag_context)
                else:
                    st.info("No RAG context retrieved.")


# -----------------------------
# Tab 2: Dashboard
# -----------------------------

with tab2:
    st.subheader("Operations Dashboard")

    st.markdown(
        """
        This dashboard uses fixed SQL skills, so it works even before the LLM agent is configured.
        """
    )

    try:
        stats = get_summary_stats()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Buildings", int(stats["building_count"]["count"][0]))
        col2.metric("Total Rooms", int(stats["room_count"]["count"][0]))
        col3.metric("Available Rooms", int(stats["available_room_count"]["count"][0]))
        col4.metric("Events", int(stats["event_count"]["count"][0]))
        col5.metric("Total Revenue", f"${stats['total_revenue']['total'][0]}")

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown("### Revenue by Service Type")
            service_df = revenue_by_service()
            st.dataframe(service_df, use_container_width=True)

            if not service_df.empty and "serviceType" in service_df.columns:
                chart_df = service_df.set_index("serviceType")
                st.bar_chart(chart_df)

        with right:
            st.markdown("### Room Status Summary")
            status_df = room_status_summary()
            st.dataframe(status_df, use_container_width=True)

            if not status_df.empty and "roomStatus" in status_df.columns:
                chart_status = status_df.set_index("roomStatus")
                st.bar_chart(chart_status)

        st.divider()

        st.markdown("### Recent Access Logs")
        access_df = recent_access_logs(limit=50)
        st.dataframe(access_df, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard error: {e}")
        st.info(
            "Check whether `hotel.db` is in the root folder and whether the table names match your database."
        )


# -----------------------------
# Tab 3: Build / Test ChromaDB
# -----------------------------

with tab3:
    st.subheader("Build / Test ChromaDB RAG")

    st.markdown(
        """
        This tab builds a ChromaDB vector store from your `knowledge_base/*.md` files.  
        On Streamlit Cloud, you may need to rebuild ChromaDB after deployment or app restart.
        """
    )

    col_build, col_note = st.columns([1, 2])

    with col_build:
        if st.button("Build / Rebuild ChromaDB", type="primary"):
            with st.spinner("Building ChromaDB from knowledge_base markdown files..."):
                try:
                    build_chroma()
                    st.success("ChromaDB built successfully.")
                except Exception as e:
                    st.error(f"ChromaDB build error: {e}")

    with col_note:
        st.info(
            """
            If retrieval returns no useful context, click **Build / Rebuild ChromaDB** first.
            """
        )

    st.divider()

    test_question = st.text_input(
        "Enter a question to preview retrieved ChromaDB context",
        value="Check suspicious access card logs",
    )

    if st.button("Retrieve ChromaDB Context"):
        with st.spinner("Retrieving semantic context from ChromaDB..."):
            try:
                context = retrieve_context_chroma(test_question)
                if context:
                    st.text(context)
                else:
                    st.warning("No context retrieved. Try rebuilding ChromaDB first.")
            except Exception as e:
                st.error(f"ChromaDB retrieval error: {e}")
                st.info("Try clicking Build / Rebuild ChromaDB first.")


# -----------------------------
# Tab 4: Database Schema
# -----------------------------

with tab4:
    st.subheader("Database Schema")

    st.markdown(
        """
        This schema is automatically read from `hotel.db`.  
        The SQL Agent uses this schema to avoid inventing table or column names.
        """
    )

    try:
        schema_text = get_database_schema()
        st.text(schema_text)
    except Exception as e:
        st.error(f"Schema loading error: {e}")
        st.info("Make sure `hotel.db` exists in the root folder.")


# -----------------------------
# Tab 5: About Skills
# -----------------------------

with tab5:
    st.subheader("HotelMind Skills")

    st.markdown(
        """
        HotelMind is organized as a skill-based AI agent system.

        ### Main Skills

        | Skill | File | Purpose |
        |---|---|---|
        | ChromaDB RAG Skill | `skills/chroma_rag_skill.py` | Retrieves relevant hotel schema, rules, KPI definitions, and anomaly rules |
        | SQL Generation Skill | `skills/sql_generation_skill.py` | Runs the full workflow from user question to final answer |
        | Fixed Report Skill | `skills/fixed_report_skill.py` | Provides dashboard queries that work without LLM |
        | SQL Safety QC Skill | `agent/qc_agent.py` | Blocks dangerous SQL and only allows `SELECT` |
        | SQL Agent | `agent/sql_agent.py` | Uses an LLM to generate SQLite-compatible SQL |
        | Analyst Agent | `agent/analyst_agent.py` | Explains query results in hotel operations language |
        | Database Tool | `tools/db_tool.py` | Executes SQL against `hotel.db` |
        | Schema Tool | `tools/schema_tool.py` | Reads database tables and columns |
        """
    )

    st.markdown(
        """
        ### Example Workflow

        ```text
        User question
        ↓
        ChromaDB RAG Skill
        ↓
        SQL Agent generates SELECT query
        ↓
        SQL Safety QC checks query
        ↓
        Database Tool queries hotel.db
        ↓
        Analyst Agent explains result
        ↓
        Final manager-friendly answer
        ```
        """
    )

    st.markdown(
        """
        ### Suggested Demo Questions

        - Which service types generate the most revenue?
        - Show the top 10 rooms by total revenue.
        - Show recent card access logs.
        - Which billing parties have the highest total charges?
        - Show event room usage by date.
        - Find guests with multiple stays.
        - Which events have the highest estimated attendance?
        """
    )
