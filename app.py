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
from tools.db_tool import run_query


st.set_page_config(
    page_title="HotelMind AI Growth Copilot",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Assets
# ============================================================

def image_to_base64(path: str):
    file_path = Path(path)
    if not file_path.exists():
        return None
    return base64.b64encode(file_path.read_bytes()).decode()


def get_img(name: str):
    for folder in ["assets", "images", "."]:
        encoded = image_to_base64(f"{folder}/{name}")
        if encoded:
            return f"data:image/jpeg;base64,{encoded}"
    return None


IMG_HERO = get_img("resort-hero.jpg")
IMG_LOBBY = get_img("lobby.jpg")
IMG_BUDGET = get_img("room-budget.jpg")
IMG_CLASSIC = get_img("room-classic.jpg")
IMG_DELUXE = get_img("room-deluxe.jpg")
IMG_PREMIUM = get_img("room-premium.jpg")
IMG_SUITE = get_img("room-suite.jpg")
IMG_POOL = get_img("pool-view.jpg")
IMG_MEETING = get_img("meeting-room.jpg")
IMG_DINING = get_img("dining.jpg")


def bg_image(img, overlay="rgba(6,40,61,0.72)"):
    if img:
        return f"linear-gradient(120deg, {overlay}, rgba(6,40,61,0.18)), url('{img}')"
    return "linear-gradient(120deg, #06283d, #0f6f8f, #61d4d4)"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>
    :root {{
        --navy: #06283d;
        --deep: #08384f;
        --ocean: #0f6f8f;
        --aqua: #61d4d4;
        --sand: #f5efe6;
        --cream: #fffaf1;
        --white: #ffffff;
        --text: #1f2933;
        --muted: #607080;
        --line: #dbe8ec;
        --danger: #d94848;
        --warning: #d18b00;
        --success: #188a5b;
        --shadow: 0 16px 36px rgba(6, 40, 61, 0.13);
    }}

    .stApp {{
        background: linear-gradient(180deg, #f6fbfc 0%, #f5efe6 100%);
        color: var(--text);
    }}

    header[data-testid="stHeader"] {{
        background: rgba(255,255,255,0);
    }}

    div[data-testid="stToolbar"] {{
        visibility: hidden;
        height: 0%;
        position: fixed;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1380px;
    }}

    section[data-testid="stSidebar"] {{
        background: #06283d;
    }}

    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .hero {{
        background-image: {bg_image(IMG_HERO or IMG_LOBBY)};
        background-size: cover;
        background-position: center;
        border-radius: 22px;
        padding: 36px 38px;
        box-shadow: var(--shadow);
        margin-bottom: 22px;
    }}

    .hero h1 {{
        color: white;
        font-size: 2.45rem;
        font-weight: 950;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }}

    .hero p {{
        color: #eefcff;
        max-width: 850px;
        line-height: 1.62;
        font-size: 1.03rem;
        margin: 0;
    }}

    .badge-row {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 18px;
    }}

    .badge {{
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.30);
        color: white;
        padding: 7px 12px;
        border-radius: 999px;
        font-weight: 850;
        font-size: 0.82rem;
    }}

    .section-head {{
        margin: 28px 0 16px 0;
    }}

    .eyebrow {{
        color: var(--ocean);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 950;
    }}

    .section-head h2 {{
        color: var(--navy);
        font-size: 1.75rem;
        font-weight: 950;
        margin: 4px 0 6px 0;
    }}

    .section-head p {{
        color: var(--muted);
        margin: 0;
        line-height: 1.55;
    }}

    .metric-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 18px;
        padding: 20px 22px;
        min-height: 120px;
    }}

    .metric-label {{
        color: var(--muted);
        font-size: 0.80rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .metric-value {{
        color: var(--navy);
        font-size: 2.05rem;
        font-weight: 950;
        margin-top: 8px;
    }}

    .metric-note {{
        color: var(--muted);
        font-size: 0.86rem;
        margin-top: 4px;
    }}

    .copilot-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 22px;
        padding: 28px;
        margin-top: 16px;
    }}

    .copilot-title {{
        color: var(--navy);
        font-size: 1.45rem;
        font-weight: 950;
        margin-bottom: 8px;
    }}

    .copilot-sub {{
        color: var(--muted);
        line-height: 1.6;
        margin-bottom: 16px;
    }}

    .chip-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 12px 0 18px 0;
    }}

    .chip {{
        background: #eefafa;
        border: 1px solid #c9f0f0;
        color: var(--navy);
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 850;
    }}

    .answer-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 20px;
        padding: 26px;
        margin-top: 20px;
    }}

    .answer-card h3 {{
        color: var(--navy);
        font-size: 1.34rem;
        font-weight: 950;
        margin: 4px 0 14px 0;
    }}

    .mode-pill, .intent-pill {{
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.80rem;
        font-weight: 850;
        margin-right: 8px;
        margin-bottom: 10px;
    }}

    .mode-pill {{
        background: var(--sand);
        color: var(--navy);
    }}

    .intent-pill {{
        background: var(--navy);
        color: white;
    }}

    .answer-main {{
        background: #f4fbfb;
        border-left: 5px solid var(--aqua);
        border-radius: 12px;
        padding: 18px 20px;
        line-height: 1.68;
        font-size: 1rem;
    }}

    .action-panel {{
        background: #06283d;
        border-radius: 20px;
        box-shadow: var(--shadow);
        padding: 24px;
        color: white;
        margin-top: 16px;
    }}

    .action-panel h3 {{
        color: white;
        font-size: 1.18rem;
        font-weight: 950;
        margin: 0 0 14px 0;
    }}

    .action-item {{
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        padding: 13px 14px;
        border-radius: 14px;
        margin-bottom: 12px;
        line-height: 1.48;
    }}

    .action-item b {{
        color: var(--aqua);
    }}

    .room-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
        margin-top: 18px;
    }}

    .room-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 20px;
        overflow: hidden;
        display: grid;
        grid-template-columns: 42% 58%;
        min-height: 190px;
    }}

    .room-img {{
        background-size: cover;
        background-position: center;
        min-height: 190px;
    }}

    .room-body {{
        padding: 18px 20px;
    }}

    .room-title {{
        color: var(--navy);
        font-size: 1.18rem;
        font-weight: 950;
        margin-bottom: 4px;
    }}

    .room-type {{
        color: var(--ocean);
        font-weight: 900;
        font-size: 0.92rem;
        margin-bottom: 9px;
    }}

    .room-meta {{
        color: var(--muted);
        line-height: 1.52;
        font-size: 0.92rem;
    }}

    .status {{
        display: inline-block;
        background: var(--ocean);
        color: white;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.78rem;
        font-weight: 850;
        margin-top: 10px;
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 18px;
    }}

    .insight-tile {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 18px;
        padding: 20px;
    }}

    .insight-tile .label {{
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 900;
    }}

    .insight-tile .value {{
        color: var(--navy);
        font-size: 1.7rem;
        font-weight: 950;
        margin-top: 8px;
    }}

    .insight-tile .desc {{
        color: var(--muted);
        margin-top: 7px;
        line-height: 1.45;
    }}

    .risk-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }}

    .risk-high {{
        border-left: 7px solid var(--danger);
    }}

    .risk-medium {{
        border-left: 7px solid var(--warning);
    }}

    .risk-low {{
        border-left: 7px solid var(--success);
    }}

    .risk-title {{
        color: var(--navy);
        font-weight: 950;
        font-size: 1.05rem;
        margin-bottom: 5px;
    }}

    .risk-meta {{
        color: var(--muted);
        line-height: 1.48;
    }}

    .module-card {{
        background: white;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        border-radius: 20px;
        overflow: hidden;
        min-height: 280px;
        margin-bottom: 18px;
    }}

    .module-img {{
        height: 145px;
        background-size: cover;
        background-position: center;
    }}

    .module-body {{
        padding: 20px 22px 22px;
    }}

    .module-body h3 {{
        color: var(--navy);
        font-size: 1.22rem;
        font-weight: 950;
        margin: 0 0 8px 0;
    }}

    .module-body p {{
        color: var(--muted);
        line-height: 1.5;
        margin: 0 0 16px 0;
    }}

    div.stButton > button:first-child {{
        background: var(--ocean);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.62rem 1.15rem;
        font-weight: 900;
    }}

    div.stButton > button:first-child:hover {{
        background: var(--aqua);
        color: var(--navy);
        border: none;
    }}

    .stDataFrame {{
        background: white;
        border-radius: 14px;
    }}

    @media (max-width: 1000px) {{
        .room-grid, .kpi-grid {{
            grid-template-columns: 1fr;
        }}
        .room-card {{
            grid-template-columns: 1fr;
        }}
        .hero h1 {{
            font-size: 1.95rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Backend helpers
# ============================================================

def has_openai_key() -> bool:
    try:
        if st.secrets.get("OPENAI_API_KEY"):
            return True
    except Exception:
        pass
    return bool(os.getenv("OPENAI_API_KEY"))


def get_stat(stats, key, col):
    try:
        return stats[key][col][0]
    except Exception:
        return 0


def classify_room_type(base_rate):
    try:
        rate = float(base_rate)
    except Exception:
        return "Guest Room"

    if rate <= 200:
        return "Cozy Standard Room"
    if rate <= 300:
        return "Classic Guest Room"
    if rate <= 400:
        return "Deluxe Resort Room"
    if rate <= 550:
        return "Premium Ocean View Room"
    return "Signature Suite"


def room_image_by_rate(row, pool=False):
    if pool and IMG_POOL:
        return IMG_POOL

    try:
        rate = float(row.get("baseRate", 0))
    except Exception:
        rate = 0

    if rate <= 200:
        return IMG_BUDGET or IMG_CLASSIC or IMG_LOBBY or IMG_HERO
    if rate <= 300:
        return IMG_CLASSIC or IMG_BUDGET or IMG_LOBBY or IMG_HERO
    if rate <= 400:
        return IMG_DELUXE or IMG_CLASSIC or IMG_LOBBY or IMG_HERO
    if rate <= 550:
        return IMG_PREMIUM or IMG_DELUXE or IMG_LOBBY or IMG_HERO
    return IMG_SUITE or IMG_PREMIUM or IMG_LOBBY or IMG_HERO


def metric_card(label, value, note):
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


def section_head(eyebrow, title, desc):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="eyebrow">{eyebrow}</div>
            <h2>{title}</h2>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        """
        <div class="hero">
            <h1>HotelMind AI Growth Copilot</h1>
            <p>
                An internal AI agent for hotel managers to grow revenue, improve room utilization,
                review billing exposure, monitor access activity, and generate daily operating briefs.
            </p>
            <div class="badge-row">
                <span class="badge">Daily Operating Brief</span>
                <span class="badge">Room Revenue Growth</span>
                <span class="badge">Dining & Upsell Strategy</span>
                <span class="badge">Billing Risk Review</span>
                <span class="badge">Access Audit</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_question(question, use_llm=False):
    if use_llm:
        if not has_openai_key():
            return {
                "success": False,
                "mode": "LLM Agent Mode",
                "intent": "Dynamic Question",
                "dataframe": None,
                "analysis": "LLM Agent Mode is unavailable because the OpenAI API key or quota is not ready. Use Smart Skills Mode for free hotel operations workflows.",
            }

        result = answer_with_generated_sql(question)
        result["mode"] = "LLM Agent Mode"
        result["intent"] = "Dynamic Question"
        return result

    return get_fixed_demo_answer(question)


# ============================================================
# Data functions for productized views
# ============================================================

def get_available_rooms():
    return get_fixed_demo_answer("Which rooms are currently available?")


def get_pool_rooms():
    return get_fixed_demo_answer("Which rooms are near the pool?")


def get_revenue_result():
    return get_fixed_demo_answer("Which service types generate the most revenue?")


def get_billing_result():
    return get_fixed_demo_answer("Which billing parties have the highest total charges?")


def get_access_result():
    return get_fixed_demo_answer("Show recent card access logs.")


def get_event_result():
    return get_fixed_demo_answer("Show event room usage by date.")


def get_daily_brief():
    stats = get_summary_stats()
    rev = revenue_by_service()
    status = room_status_summary()

    total_rooms = int(get_stat(stats, "room_count", "count"))
    available = int(get_stat(stats, "available_room_count", "count"))
    events = int(get_stat(stats, "event_count", "count"))
    revenue = get_stat(stats, "total_revenue", "total")

    occupied = 0
    cleaning = 0
    renovation = 0

    if isinstance(status, pd.DataFrame) and not status.empty:
        lookup = dict(zip(status["roomStatus"], status["count"]))
        occupied = int(lookup.get("occupied", 0))
        cleaning = int(lookup.get("cleaning", 0))
        renovation = int(lookup.get("renovation", 0))

    top_service = "N/A"
    top_revenue = 0
    if isinstance(rev, pd.DataFrame) and not rev.empty:
        top_service = rev.iloc[0]["serviceType"]
        top_revenue = rev.iloc[0]["revenue"]

    analysis = (
        f"Today’s operating brief: the hotel has {available} available rooms out of {total_rooms}, "
        f"with {occupied} occupied rooms, {cleaning} in cleaning, and {renovation} under renovation. "
        f"Recorded revenue is ${revenue}, led by {top_service} revenue at ${top_revenue}. "
        f"The manager should prioritize ready-room assignment, protect high-rate inventory, and review event or dining upsell opportunities."
    )

    return {
        "success": True,
        "mode": "Smart Skills Mode",
        "intent": "Daily Operating Brief",
        "analysis": analysis,
        "dataframe": pd.DataFrame([
            {"Metric": "Total rooms", "Value": total_rooms},
            {"Metric": "Available rooms", "Value": available},
            {"Metric": "Occupied rooms", "Value": occupied},
            {"Metric": "Cleaning rooms", "Value": cleaning},
            {"Metric": "Renovation rooms", "Value": renovation},
            {"Metric": "Scheduled events", "Value": events},
            {"Metric": "Recorded revenue", "Value": revenue},
            {"Metric": "Top revenue source", "Value": top_service},
        ])
    }


def get_dining_strategy():
    rev = revenue_by_service()

    food_revenue = 0
    event_revenue = 0
    room_revenue = 0

    if isinstance(rev, pd.DataFrame) and not rev.empty:
        for _, row in rev.iterrows():
            service = str(row["serviceType"]).lower()
            amount = float(row["revenue"])
            if service == "food":
                food_revenue = amount
            elif service == "event":
                event_revenue = amount
            elif service == "room":
                room_revenue = amount

    if food_revenue < event_revenue:
        positioning = "Event-led dining growth"
        recommendation = (
            "Food revenue is currently below event revenue, which suggests a clear opportunity to attach dining packages "
            "to meetings, group events, and conference room usage. The hotel should position dining as a convenient event add-on."
        )
    else:
        positioning = "Standalone dining strength"
        recommendation = (
            "Food revenue is already meaningful relative to event revenue. The hotel can strengthen restaurant positioning "
            "through premium breakfast, seasonal tasting menus, and room-plus-dining bundles."
        )

    analysis = (
        f"Dining positioning recommendation: {positioning}. "
        f"Food revenue is ${food_revenue}, event revenue is ${event_revenue}, and room revenue is ${room_revenue}. "
        f"{recommendation}"
    )

    df = pd.DataFrame([
        {"Revenue Area": "Room", "Revenue": room_revenue, "Growth Role": "Core occupancy driver"},
        {"Revenue Area": "Event", "Revenue": event_revenue, "Growth Role": "Group demand and meeting-room packages"},
        {"Revenue Area": "Food", "Revenue": food_revenue, "Growth Role": "Restaurant, breakfast, catering, and upsell opportunity"},
    ])

    return {
        "success": True,
        "mode": "Smart Skills Mode",
        "intent": "Dining & Upsell Strategy",
        "analysis": analysis,
        "dataframe": df
    }


# ============================================================
# Product renderers
# ============================================================

def render_answer(result):
    success = result.get("success", False)
    mode = result.get("mode", "Smart Skills Mode")
    intent = result.get("intent", "Hotel Operations")
    analysis = result.get("analysis", "No recommendation generated.")

    st.markdown(
        f"""
        <div class="answer-card">
            <span class="mode-pill">{mode}</span>
            <span class="intent-pill">{intent}</span>
            <h3>{"HotelMind Recommendation" if success else "HotelMind could not complete this request"}</h3>
            <div class="answer-main">{analysis}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_room_cards(df, max_rooms=6, pool=False):
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("No matching rooms found.")
        return

    rows = df.head(max_rooms).to_dict("records")
    html = "<div class='room-grid'>"

    for row in rows:
        room = row.get("roomNumber", "")
        building = row.get("buildingName", "")
        wing = row.get("wingName", "")
        floor = row.get("floorNumber", "")
        rate = row.get("baseRate", "")
        status = row.get("roomStatus", "available")
        room_type = classify_room_type(rate)
        img = room_image_by_rate(row, pool=pool)

        if img:
            bg = f"url('{img}')"
        else:
            bg = "linear-gradient(120deg, #06283d, #0f6f8f, #61d4d4)"

        html += f"""
        <div class="room-card">
            <div class="room-img" style="background-image: {bg};"></div>
            <div class="room-body">
                <div class="room-title">Room {room}</div>
                <div class="room-type">{room_type}</div>
                <div class="room-meta">
                    {building} · {wing} Wing · Floor {floor}<br>
                    Base rate: ${rate}
                </div>
                <span class="status">{status}</span>
            </div>
        </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_revenue_cards(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return

    top = df.head(3).to_dict("records")
    html = "<div class='kpi-grid'>"

    for i, row in enumerate(top, start=1):
        html += f"""
        <div class="insight-tile">
            <div class="label">Revenue Driver #{i}</div>
            <div class="value">{row.get("serviceType", "")}</div>
            <div class="desc">${row.get("revenue", 0)} recorded revenue</div>
        </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_billing_risk_cards(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("No billing records found.")
        return

    rows = df.head(5).to_dict("records")

    for i, row in enumerate(rows):
        total = float(row.get("totalCharges", 0))
        risk_class = "risk-high" if i == 0 else "risk-medium" if i < 3 else "risk-low"

        st.markdown(
            f"""
            <div class="risk-card {risk_class}">
                <div class="risk-title">{row.get("billingParty", "Billing Party")}</div>
                <div class="risk-meta">
                    Total charges: ${total} · Charge count: {row.get("chargeCount", "-")}<br>
                    Recommended action: review charge ownership and payment follow-up priority.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_event_cards(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("No event records found.")
        return

    rows = df.head(5).to_dict("records")

    for row in rows:
        st.markdown(
            f"""
            <div class="risk-card risk-medium">
                <div class="risk-title">Event {row.get("eventId", "")}</div>
                <div class="risk-meta">
                    Date: {row.get("startDate", "")} to {row.get("endDate", "")}<br>
                    Room: {row.get("roomNumber", "")} · Usage slot: {row.get("usageSlot", "")}<br>
                    Estimated attendance: {row.get("estimatedAttendance", "N/A")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_action_panel(intent):
    intent = (intent or "").lower()

    if "daily" in intent:
        actions = [
            ("Protect high-rate inventory", "Hold premium rooms for late-arriving high-value guests or event blocks."),
            ("Review room readiness", "Cleaning and renovation rooms should be checked before peak arrival time."),
            ("Push attach-rate growth", "Use room and event demand to upsell dining, spa, and parking."),
        ]
    elif "dining" in intent:
        actions = [
            ("Bundle dining with events", "Create catering or lunch packages for meeting-room bookings."),
            ("Create room-plus-breakfast offers", "Use available rooms to promote breakfast-inclusive packages."),
            ("Position dining as convenience", "Market the restaurant as the easiest option for event attendees and hotel guests."),
        ]
    elif "revenue" in intent:
        actions = [
            ("Prioritize top services", "Focus manager attention on the largest revenue categories first."),
            ("Build upsell bundles", "Attach food, spa, and parking to rooms or events."),
            ("Track low-revenue services", "Use smaller categories as incremental margin opportunities."),
        ]
    elif "billing" in intent:
        actions = [
            ("Review top balances", "Start with the largest billing parties."),
            ("Confirm responsibility", "Check whether charges are assigned to the correct guest or organization."),
            ("Prepare front-office follow-up", "Use the list for payment reminders or dispute prevention."),
        ]
    elif "access" in intent:
        actions = [
            ("Review recent entries", "Check latest access activity for unusual patterns."),
            ("Escalate exceptions", "Flag suspicious timing or room mismatch for security review."),
            ("Support guest service", "Use logs to resolve lockout or entry disputes."),
        ]
    else:
        actions = [
            ("Review manager recommendation", "Use the answer as a decision support view."),
            ("Open supporting data if needed", "Detailed tables are available only when helpful."),
            ("Use Smart Skills first", "Stable workflows run without API cost."),
        ]

    html = "<div class='action-panel'><h3>Recommended Next Actions</h3>"
    for title, desc in actions:
        html += f"<div class='action-item'><b>{title}</b><br>{desc}</div>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def module_card(title, desc, img):
    if img:
        bg = f"url('{img}')"
    else:
        bg = "linear-gradient(120deg, #06283d, #0f6f8f, #61d4d4)"

    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-img" style="background-image: {bg};"></div>
            <div class="module-body">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def supporting_data(df):
    if isinstance(df, pd.DataFrame):
        with st.expander("View supporting data"):
            st.dataframe(df, use_container_width=True)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.markdown("## 🏨 HotelMind")
st.sidebar.markdown("Internal AI growth copilot for hotel managers.")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Growth Copilot",
        "Daily Brief",
        "Room Revenue",
        "Dining & Upsell",
        "Billing Risk",
        "Access Audit",
        "Event Planning",
        "Admin",
    ],
)

st.sidebar.divider()
st.sidebar.markdown("### Product Positioning")
st.sidebar.markdown("**Primary user:** hotel manager")
st.sidebar.markdown("**Goal:** revenue growth + operational control")
st.sidebar.markdown("**Default mode:** Smart Skills, no API cost")
st.sidebar.markdown(f"**LLM status:** {'Ready' if has_openai_key() else 'No quota / no key'}")


# ============================================================
# Main
# ============================================================

hero()


# ============================================================
# Page: Growth Copilot
# ============================================================

if page == "Growth Copilot":
    try:
        stats = get_summary_stats()
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("Available Rooms", int(get_stat(stats, "available_room_count", "count")), "Ready for assignment")
        with c2:
            metric_card("Total Revenue", f"${get_stat(stats, 'total_revenue', 'total')}", "Recorded charges")
        with c3:
            metric_card("Scheduled Events", int(get_stat(stats, "event_count", "count")), "Group demand opportunities")
        with c4:
            metric_card("Total Rooms", int(get_stat(stats, "room_count", "count")), "Inventory base")
    except Exception:
        pass

    left, right = st.columns([2.1, 1])

    with left:
        st.markdown(
            """
            <div class="copilot-card">
                <div class="copilot-title">Ask HotelMind</div>
                <div class="copilot-sub">
                    Ask an operational or revenue-growth question. The agent returns manager-facing recommendations,
                    visual cards, and supporting data without exposing SQL.
                </div>
                <div class="chip-row">
                    <span class="chip">Generate today’s operating brief</span>
                    <span class="chip">Find revenue growth opportunities</span>
                    <span class="chip">Recommend rooms for assignment</span>
                    <span class="chip">Review billing risk</span>
                    <span class="chip">Improve dining revenue</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "Assistant mode",
            ["Smart Skills Mode - free", "LLM Agent Mode - uses API credits"],
            index=0,
            horizontal=True,
        )

        examples = [
            "Generate today’s operating brief.",
            "Which service types generate the most revenue?",
            "Which rooms are currently available?",
            "Which rooms are near the pool?",
            "How should we position dining to increase revenue?",
            "Which billing parties have the highest total charges?",
            "Show recent card access logs.",
            "Show event room usage by date.",
        ]

        selected = st.selectbox("Quick manager request", [""] + examples)

        question = st.text_area(
            "Type your question",
            value=selected,
            placeholder="Example: How can we grow revenue today using available rooms and dining upsell?",
            height=120,
        )

        if st.button("Ask HotelMind", type="primary"):
            if not question.strip():
                st.error("Please enter a question.")
            else:
                q = question.lower()

                if "daily" in q or "brief" in q or "operating" in q:
                    result = get_daily_brief()
                    render_answer(result)
                    render_action_panel(result.get("intent"))
                    supporting_data(result.get("dataframe"))

                elif "dining" in q or "restaurant" in q or "food" in q or "upsell" in q:
                    result = get_dining_strategy()
                    render_answer(result)
                    render_action_panel(result.get("intent"))
                    df = result.get("dataframe")
                    if isinstance(df, pd.DataFrame):
                        st.bar_chart(df.set_index("Revenue Area")["Revenue"])
                    supporting_data(df)

                else:
                    result = run_question(question.strip(), use_llm=mode.startswith("LLM"))
                    render_answer(result)

                    lower_q = question.lower()
                    df = result.get("dataframe")

                    if any(k in lower_q for k in ["room", "available", "pool"]):
                        render_room_cards(df, max_rooms=6, pool=("pool" in lower_q))

                    elif "revenue" in lower_q:
                        render_revenue_cards(df)
                        if isinstance(df, pd.DataFrame) and "serviceType" in df.columns:
                            st.bar_chart(df.set_index("serviceType")["revenue"])

                    elif "billing" in lower_q:
                        render_billing_risk_cards(df)

                    elif "event" in lower_q:
                        render_event_cards(df)

                    render_action_panel(result.get("intent"))
                    supporting_data(df)

    with right:
        render_action_panel("daily")


# ============================================================
# Page: Daily Brief
# ============================================================

elif page == "Daily Brief":
    section_head(
        "Operating Brief",
        "Daily manager briefing",
        "A concise morning-style summary for room readiness, revenue, events, and growth priorities.",
    )

    result = get_daily_brief()
    render_answer(result)
    render_action_panel(result.get("intent"))

    df = result.get("dataframe")
    if isinstance(df, pd.DataFrame):
        c1, c2, c3 = st.columns(3)
        for idx, row in df.head(6).iterrows():
            with [c1, c2, c3][idx % 3]:
                metric_card(row["Metric"], row["Value"], "Daily operating signal")

    supporting_data(df)


# ============================================================
# Page: Room Revenue
# ============================================================

elif page == "Room Revenue":
    section_head(
        "Room Growth",
        "Room assignment and revenue opportunity",
        "Use visual room cards to support front-desk decisions and protect premium inventory.",
    )

    c1, c2 = st.columns(2)

    with c1:
        module_card(
            "Available Room Inventory",
            "Find rooms ready for assignment and use room type labels to guide front-desk decisions.",
            IMG_DELUXE or IMG_CLASSIC or IMG_LOBBY or IMG_HERO,
        )
        if st.button("Show Available Rooms"):
            result = get_available_rooms()
            render_answer(result)
            render_room_cards(result.get("dataframe"), max_rooms=6)
            render_action_panel(result.get("intent"))
            supporting_data(result.get("dataframe"))

    with c2:
        module_card(
            "Pool-Proximity Upsell",
            "Recommend pool-adjacent rooms for leisure guests and potential room-rate upgrades.",
            IMG_POOL or IMG_PREMIUM or IMG_HERO,
        )
        if st.button("Show Pool-Proximity Rooms"):
            result = get_pool_rooms()
            render_answer(result)
            render_room_cards(result.get("dataframe"), max_rooms=6, pool=True)
            render_action_panel(result.get("intent"))
            supporting_data(result.get("dataframe"))


# ============================================================
# Page: Dining & Upsell
# ============================================================

elif page == "Dining & Upsell":
    section_head(
        "Dining Strategy",
        "Restaurant positioning and upsell opportunities",
        "Position dining as a revenue growth lever connected to rooms, events, and guest convenience.",
    )

    module_card(
        "Dining & Event Upsell Strategy",
        "Use revenue mix to decide whether dining should be positioned as event catering, room package add-on, or standalone restaurant experience.",
        IMG_DINING or IMG_LOBBY or IMG_HERO,
    )

    result = get_dining_strategy()
    render_answer(result)
    render_action_panel(result.get("intent"))

    df = result.get("dataframe")
    if isinstance(df, pd.DataFrame):
        st.bar_chart(df.set_index("Revenue Area")["Revenue"])
    supporting_data(df)


# ============================================================
# Page: Billing Risk
# ============================================================

elif page == "Billing Risk":
    section_head(
        "Billing Risk",
        "Charge exposure and payment follow-up",
        "Identify billing parties with the highest total charges and prioritize review.",
    )

    result = get_billing_result()
    render_answer(result)
    render_billing_risk_cards(result.get("dataframe"))
    render_action_panel(result.get("intent"))
    supporting_data(result.get("dataframe"))


# ============================================================
# Page: Access Audit
# ============================================================

elif page == "Access Audit":
    section_head(
        "Access Audit",
        "Guest access activity review",
        "Monitor recent card access activity for operational support and security review.",
    )

    result = get_access_result()
    render_answer(result)
    render_action_panel(result.get("intent"))
    supporting_data(result.get("dataframe"))


# ============================================================
# Page: Event Planning
# ============================================================

elif page == "Event Planning":
    section_head(
        "Event Planning",
        "Meeting-room and group event preparation",
        "Use event-room usage and attendance signals to plan staffing, service, and dining opportunities.",
    )

    module_card(
        "Event Revenue & Dining Attach",
        "Large events can drive room blocks, meeting-room usage, food service, and guest convenience packages.",
        IMG_MEETING or IMG_HERO,
    )

    result = get_event_result()
    render_answer(result)
    render_event_cards(result.get("dataframe"))
    render_action_panel(result.get("intent"))
    supporting_data(result.get("dataframe"))


# ============================================================
# Page: Admin
# ============================================================

elif page == "Admin":
    section_head(
        "Admin",
        "System configuration",
        "Backend tools for deployment and evaluation. SQL is intentionally hidden from the manager-facing product UI.",
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Build ChromaDB")
        st.write("Build the vector store from schema, KPI, business rule, and anomaly-rule documents.")
        if st.button("Build / Rebuild ChromaDB"):
            try:
                with st.spinner("Building ChromaDB..."):
                    build_chroma()
                st.success("ChromaDB built successfully.")
            except Exception as e:
                st.error(f"ChromaDB build error: {e}")

    with c2:
        st.markdown("### Test Retrieval")
        q = st.text_input("Question for retrieval", "Check suspicious access card logs")
        if st.button("Retrieve Context"):
            try:
                context = retrieve_context_chroma(q)
                if context:
                    st.success("RAG context retrieved successfully.")
                else:
                    st.warning("No context retrieved. Build ChromaDB first.")
            except Exception as e:
                st.error(f"Retrieval error: {e}")

    st.divider()

    st.markdown("### Architecture Summary")
    st.markdown(
        """
        **HotelMind is designed as an internal hotel growth copilot.**

        - **Smart Skills Mode:** stable, predefined SQL workflows for common manager questions  
        - **LLM Agent Mode:** optional natural-language to SQL for flexible ad-hoc analysis  
        - **ChromaDB RAG:** schema and business-rule grounding  
        - **Manager-facing UI:** recommendations, cards, charts, and operating briefs  
        - **SQL hidden by design:** managers see decisions, not backend code  
        """
    )
