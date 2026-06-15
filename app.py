import os
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from skills.fixed_report_skill import (
    get_summary_stats,
    revenue_by_service,
    room_status_summary,
    recent_access_logs,
    get_fixed_demo_answer,
)
from skills.sql_generation_skill import answer_with_generated_sql
from skills.chroma_rag_skill import retrieve_context_chroma
from data.build_chroma import build_chroma
from tools.schema_tool import get_database_schema


st.set_page_config(
    page_title="HotelMind AI Command Center",
    page_icon="🏨",
    layout="wide",
)


# =========================
# Styling
# =========================

def image_to_base64(path: str):
    file_path = Path(path)
    if not file_path.exists():
        return None
    return base64.b64encode(file_path.read_bytes()).decode()


hero_image = (
    image_to_base64("assets/resort-hero.jpg")
    or image_to_base64("images/resort-hero.jpg")
)

if hero_image:
    hero_background = f"""
        linear-gradient(90deg, rgba(6,40,61,0.82), rgba(6,40,61,0.18)),
        url("data:image/jpeg;base64,{hero_image}")
    """
else:
    hero_background = """
        linear-gradient(120deg, rgba(6,40,61,0.95), rgba(15,111,143,0.72), rgba(97,212,212,0.28))
    """


st.markdown(
    f"""
    <style>
    :root {{
        --navy: #06283d;
        --ocean: #0f6f8f;
        --aqua: #61d4d4;
        --sand: #f5efe6;
        --white: #ffffff;
        --text: #1f2933;
        --muted: #607080;
        --shadow: 0 14px 34px rgba(6, 40, 61, 0.14);
    }}

    .stApp {{
        background:
            linear-gradient(rgba(255,255,255,0.82), rgba(245,239,230,0.88)),
            {hero_background};
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(6, 40, 61, 0.96);
    }}

    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }}

    .hero {{
        min-height: 430px;
        padding: 58px 64px;
        background-image: {hero_background};
        background-size: cover;
        background-position: center;
        border-radius: 0px;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        margin-bottom: 34px;
    }}

    .hero-content {{
        max-width: 820px;
    }}

    .eyebrow {{
        color: var(--aqua);
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 0.82rem;
        margin-bottom: 12px;
    }}

    .hero h1 {{
        color: white;
        font-size: 3.65rem;
        line-height: 1.05;
        margin: 0 0 16px 0;
        font-weight: 900;
    }}

    .hero p {{
        color: #f1fbff;
        font-size: 1.13rem;
        line-height: 1.75;
        max-width: 760px;
    }}

    .hero-badges {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 26px;
    }}

    .hero-badge {{
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.38);
        color: white;
        padding: 10px 16px;
        font-weight: 800;
        backdrop-filter: blur(4px);
    }}

    .section-title {{
        margin: 34px 0 16px 0;
    }}

    .section-title .eyebrow {{
        color: var(--ocean);
    }}

    .section-title h2 {{
        font-size: 2.05rem;
        color: var(--navy);
        margin: 4px 0 8px 0;
        font-weight: 900;
    }}

    .section-title p {{
        color: var(--muted);
        margin: 0;
        font-size: 1rem;
    }}

    .metric-card {{
        background: rgba(255,255,255,0.88);
        padding: 24px;
        min-height: 142px;
        box-shadow: var(--shadow);
        border-top: 5px solid var(--ocean);
    }}

    .metric-label {{
        color: var(--muted);
        font-weight: 800;
        font-size: 0.9rem;
    }}

    .metric-value {{
        color: var(--ocean);
        font-weight: 900;
        font-size: 2.35rem;
        margin-top: 10px;
    }}

    .metric-note {{
        color: var(--muted);
        font-size: 0.88rem;
        margin-top: 8px;
    }}

    .module-card {{
        background: rgba(255,255,255,0.90);
        box-shadow: var(--shadow);
        padding: 28px;
        min-height: 230px;
        border-left: 6px solid var(--ocean);
        margin-bottom: 18px;
    }}

    .module-card h3 {{
        color: var(--navy);
        margin: 0 0 10px 0;
        font-size: 1.35rem;
        font-weight: 900;
    }}

    .module-card p {{
        color: var(--muted);
        line-height: 1.55;
        margin-bottom: 18px;
    }}

    .answer-card {{
        background: rgba(255,255,255,0.94);
        box-shadow: var(--shadow);
        padding: 30px;
        border-left: 7px solid var(--ocean);
        margin-top: 26px;
    }}

    .answer-card h3 {{
        color: var(--navy);
        font-size: 1.55rem;
        margin-top: 0;
    }}

    .insight-box {{
        background: #eefafa;
        border-left: 5px solid var(--aqua);
        padding: 18px 22px;
        margin: 18px 0;
        color: var(--text);
        line-height: 1.65;
        font-size: 1.02rem;
    }}

    .mode-pill {{
        display: inline-block;
        padding: 8px 13px;
        background: var(--sand);
        color: var(--navy);
        font-weight: 900;
        margin-right: 8px;
        font-size: 0.86rem;
    }}

    div.stButton > button:first-child {{
        background: var(--ocean);
        color: white;
        border: none;
        padding: 0.75rem 1.35rem;
        border-radius: 0;
        font-weight: 900;
    }}

    div.stButton > button:first-child:hover {{
        background: var(--aqua);
        color: var(--navy);
        border: none;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 16px;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-weight: 800;
        color: var(--navy);
    }}

    .stDataFrame {{
        background: rgba(255,255,255,0.96);
        box-shadow: var(--shadow);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Helpers
# =========================

def has_openai_key() -> bool:
    try:
        if st.secrets.get("OPENAI_API_KEY"):
            return True
    except Exception:
        pass
    return bool(os.getenv("OPENAI_API_KEY"))


def safe_value(stats, key, col):
    try:
        return stats[key][col][0]
    except Exception:
        return 0


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <div class="eyebrow">AI Operations Suite for Resort Managers</div>
                <h1>HotelMind AI Command Center</h1>
                <p>
                    Monitor hotel revenue, room readiness, billing exposure, event usage, and access activity
                    through a manager-facing AI assistant powered by SQL skills, ChromaDB RAG, and optional LLM reasoning.
                </p>
                <div class="hero-badges">
                    <div class="hero-badge">Free Demo Mode</div>
                    <div class="hero-badge">SQLite Hotel Database</div>
                    <div class="hero-badge">ChromaDB RAG</div>
                    <div class="hero-badge">Manager Insights</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="section-title">
            <div class="eyebrow">{eyebrow}</div>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_answer(result, show_table=True):
    success = result.get("success", False)
    mode = result.get("mode", "HotelMind")
    intent = result.get("intent", "Hotel Operations")

    st.markdown(
        f"""
        <div class="answer-card">
            <span class="mode-pill">{mode}</span>
            <span class="mode-pill">{intent}</span>
            <h3>{'Recommended Manager View' if success else 'HotelMind could not complete this request'}</h3>
            <div class="insight-box">{result.get("analysis", "No manager insight generated.")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = result.get("dataframe")
    if show_table and isinstance(df, pd.DataFrame):
        st.markdown("#### Supporting Data")
        st.dataframe(df, use_container_width=True)

    with st.expander("Technical Audit Trail: SQL, QC, and backend execution"):
        st.markdown("**Selected / Generated SQL**")
        if result.get("sql"):
            st.code(result["sql"], language="sql")
        else:
            st.info("No SQL was generated or selected.")

        st.markdown("**SQL Safety Check**")
        if success:
            st.success(result.get("qc_message", "Query passed safety check."))
        else:
            st.error(result.get("qc_message", "Query did not pass safety check."))

        if result.get("rag_context"):
            st.markdown("**Retrieved RAG Context**")
            st.text(result.get("rag_context"))


def run_manager_question(question, use_llm=False):
    if use_llm:
        if not has_openai_key():
            return {
                "success": False,
                "mode": "LLM Agent Mode",
                "intent": "Dynamic SQL",
                "sql": "",
                "qc_message": "OpenAI API key is missing.",
                "dataframe": None,
                "analysis": "LLM Agent Mode is unavailable because the OpenAI API key is missing. Use Free Demo Mode to run hotel operations workflows without API cost.",
            }

        result = answer_with_generated_sql(question)
        result["mode"] = "LLM Agent Mode"
        result["intent"] = "Dynamic SQL Query"
        return result

    return get_fixed_demo_answer(question)


# =========================
# Sidebar
# =========================

st.sidebar.markdown("## 🏨 HotelMind")
st.sidebar.markdown("Manager-facing AI command center for hotel operations.")
st.sidebar.divider()

st.sidebar.markdown("### System Status")
st.sidebar.markdown("**Database:** `hotel.db`")
st.sidebar.markdown("**RAG:** ChromaDB")
st.sidebar.markdown("**Free Demo:** Enabled")
st.sidebar.markdown(f"**LLM Agent:** {'Ready' if has_openai_key() else 'No API / quota'}")

st.sidebar.divider()
st.sidebar.markdown("### Manager Questions")
st.sidebar.markdown(
    """
    - Revenue performance  
    - Room readiness  
    - Billing review  
    - Access audit  
    - Event usage  
    - Guest stay history  
    """
)


# =========================
# Main
# =========================

render_hero()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Manager Assistant",
        "Executive Dashboard",
        "Operations Modules",
        "RAG & Data",
        "System Design",
    ]
)


# =========================
# Tab 1: Manager Assistant
# =========================

with tab1:
    section_title(
        "AI ASSISTANT",
        "Ask HotelMind like a hotel manager",
        "Use natural language to request revenue, room, billing, access, event, or guest insights. SQL and backend details are hidden unless you open the technical audit trail.",
    )

    col_mode, col_info = st.columns([1, 2])

    with col_mode:
        agent_mode = st.radio(
            "Agent mode",
            ["Free Demo Mode", "LLM Agent Mode"],
            index=0,
        )

    with col_info:
        if agent_mode == "Free Demo Mode":
            st.info("Free Demo Mode uses fixed SQL skills and does not call OpenAI, so it does not cost API money.")
        else:
            st.warning("LLM Agent Mode calls OpenAI to generate SQL dynamically. It may use paid API credits.")

    examples = [
        "Which service types generate the most revenue?",
        "Show room status breakdown.",
        "Which rooms are currently available?",
        "Show recent card access logs.",
        "Which billing parties have the highest total charges?",
        "Show event room usage by date.",
        "Which events have the highest estimated attendance?",
        "Which rooms are near the pool?",
        "Show guests and their stay history.",
        "Show top rooms by revenue.",
    ]

    selected = st.selectbox("Quick manager request", [""] + examples)

    question = st.text_area(
        "Or type your own hotel operations question",
        value=selected,
        placeholder="Example: Which billing parties should the front office review first?",
        height=120,
    )

    if st.button("Ask HotelMind", type="primary"):
        if not question.strip():
            st.error("Please enter a hotel operations question.")
        else:
            with st.spinner("HotelMind is preparing a manager-facing operations answer..."):
                result = run_manager_question(
                    question.strip(),
                    use_llm=(agent_mode == "LLM Agent Mode"),
                )
            render_answer(result)


# =========================
# Tab 2: Executive Dashboard
# =========================

with tab2:
    section_title(
        "EXECUTIVE OVERVIEW",
        "Today’s hotel operations snapshot",
        "A manager-facing overview of rooms, revenue, events, and operational readiness.",
    )

    try:
        stats = get_summary_stats()

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_metric_card("Buildings", int(safe_value(stats, "building_count", "count")), "Active resort properties")
        with c2:
            render_metric_card("Total Rooms", int(safe_value(stats, "room_count", "count")), "Rooms in the database")
        with c3:
            render_metric_card("Available Rooms", int(safe_value(stats, "available_room_count", "count")), "Ready for assignment")
        with c4:
            render_metric_card("Events", int(safe_value(stats, "event_count", "count")), "Scheduled group events")
        with c5:
            render_metric_card("Total Revenue", f"${safe_value(stats, 'total_revenue', 'total')}", "Recorded charges")

        st.divider()

        left, right = st.columns(2)

        with left:
            section_title("REVENUE", "Revenue by service type", "Identify the strongest revenue drivers.")
            df_rev = revenue_by_service()
            st.bar_chart(df_rev.set_index("serviceType"))
            st.dataframe(df_rev, use_container_width=True)

        with right:
            section_title("ROOMS", "Room readiness summary", "Monitor available, occupied, cleaning, and renovation rooms.")
            df_status = room_status_summary()
            st.bar_chart(df_status.set_index("roomStatus"))
            st.dataframe(df_status, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard error: {e}")


# =========================
# Tab 3: Operations Modules
# =========================

with tab3:
    section_title(
        "OPERATIONS MODULES",
        "Run common hotel management workflows",
        "These modules use backend SQL skills and return manager-facing answers without requiring OpenAI API credits.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="module-card">
                <h3>Revenue Intelligence</h3>
                <p>Review the strongest revenue drivers across room, event, food, spa, and other service categories.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Analyze Revenue Drivers"):
            render_answer(get_fixed_demo_answer("Which service types generate the most revenue?"))

    with col2:
        st.markdown(
            """
            <div class="module-card">
                <h3>Room Readiness</h3>
                <p>Understand room availability and operational status across available, occupied, cleaning, and renovation rooms.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Check Room Readiness"):
            render_answer(get_fixed_demo_answer("Show room status breakdown."))

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
            <div class="module-card">
                <h3>Access Audit</h3>
                <p>Review recent guest card access activity to support security and service operations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Review Access Logs"):
            render_answer(get_fixed_demo_answer("Show recent card access logs."))

    with col4:
        st.markdown(
            """
            <div class="module-card">
                <h3>Billing Review</h3>
                <p>Identify billing parties with the highest charge exposure for front-office review.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Review Billing Exposure"):
            render_answer(get_fixed_demo_answer("Which billing parties have the highest total charges?"))

    col5, col6 = st.columns(2)

    with col5:
        st.markdown(
            """
            <div class="module-card">
                <h3>Event Usage</h3>
                <p>Review event room usage and expected attendance to support staffing and space planning.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Review Event Usage"):
            render_answer(get_fixed_demo_answer("Show event room usage by date."))

    with col6:
        st.markdown(
            """
            <div class="module-card">
                <h3>Guest Stay History</h3>
                <p>Review guest stay patterns to support repeat-guest service and loyalty opportunities.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Review Guest Stays"):
            render_answer(get_fixed_demo_answer("Show guests and their stay history."))


# =========================
# Tab 4: RAG & Data
# =========================

with tab4:
    section_title(
        "DATA LAYER",
        "Hotel database and knowledge retrieval",
        "This section is for administrators and evaluators who want to inspect the backend data and RAG layer.",
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Build ChromaDB")
        st.write("Build a vector store from the hotel schema guide, business rules, KPI definitions, and anomaly rules.")
        if st.button("Build / Rebuild ChromaDB"):
            try:
                with st.spinner("Building ChromaDB..."):
                    build_chroma()
                st.success("ChromaDB built successfully.")
            except Exception as e:
                st.error(f"ChromaDB build error: {e}")

    with c2:
        st.markdown("### Test Retrieval")
        retrieval_question = st.text_input("Question for RAG retrieval", "Check suspicious access card logs")
        if st.button("Retrieve Knowledge Context"):
            try:
                context = retrieve_context_chroma(retrieval_question)
                if context:
                    st.text(context)
                else:
                    st.warning("No context retrieved. Build ChromaDB first.")
            except Exception as e:
                st.error(f"Retrieval error: {e}")

    st.divider()

    with st.expander("View database schema"):
        try:
            st.text(get_database_schema())
        except Exception as e:
            st.error(f"Schema error: {e}")

    with st.expander("View recent access logs sample"):
        try:
            st.dataframe(recent_access_logs(25), use_container_width=True)
        except Exception as e:
            st.error(f"Access log error: {e}")


# =========================
# Tab 5: System Design
# =========================

with tab5:
    section_title(
        "SYSTEM DESIGN",
        "Frontend and backend architecture",
        "HotelMind uses Streamlit as an integrated frontend/backend layer with modular Python skills and AI agents behind the interface.",
    )

    st.markdown(
        """
        ### Product Architecture

        **Frontend / Product UI**
        - Streamlit manager dashboard
        - Hotel operations command center
        - Manager-facing assistant interface
        - Executive dashboard and operational modules

        **Backend / Agent Logic**
        - Fixed SQL skills for free demo workflows
        - Optional LLM-generated SQL for flexible natural-language questions
        - SQL safety validation
        - SQLite database execution against `hotel.db`
        - ChromaDB RAG retrieval from hotel knowledge files

        **Three-Agent Design**
        - **SQL Agent:** generates SQL for dynamic questions
        - **QC Agent:** checks SQL safety before execution
        - **Analyst Agent:** turns results into manager-facing insights

        **Why SQL is hidden from managers**
        - Hotel managers need decisions, not raw backend traces.
        - SQL and QC are still available under the technical audit trail for evaluation and transparency.
        """
    )

    st.code(
        """
Manager Question
↓
HotelMind Product Interface
↓
Free SQL Skill or LLM SQL Agent
↓
QC Agent validates read-only SQL
↓
Database Tool queries hotel.db
↓
Manager-facing answer + supporting data
↓
Technical Audit Trail available if needed
        """,
        language="text",
    )