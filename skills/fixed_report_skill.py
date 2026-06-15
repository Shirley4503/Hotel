from tools.db_tool import run_query


def get_summary_stats():
    return {
        "building_count": run_query("SELECT COUNT(*) AS count FROM building"),
        "room_count": run_query("SELECT COUNT(*) AS count FROM room"),
        "available_room_count": run_query("SELECT COUNT(*) AS count FROM room WHERE roomStatus = 'available'"),
        "event_count": run_query("SELECT COUNT(*) AS count FROM event"),
        "total_revenue": run_query("SELECT ROUND(COALESCE(SUM(amount), 0), 2) AS total FROM charge")
    }


def revenue_by_service():
    sql = """
        SELECT s.serviceType,
               ROUND(SUM(c.amount), 2) AS revenue
        FROM charge c
        JOIN service s ON c.serviceId = s.serviceId
        GROUP BY s.serviceType
        ORDER BY revenue DESC
    """
    return run_query(sql)


def room_status_summary():
    sql = """
        SELECT roomStatus,
               COUNT(*) AS count
        FROM room
        GROUP BY roomStatus
        ORDER BY count DESC
    """
    return run_query(sql)


def recent_access_logs(limit=30):
    sql = f"""
        SELECT cal.logId,
               cal.cardId,
               p.first_name || ' ' || p.last_name AS guest,
               r.roomNumber,
               cal.accessTime,
               cal.direction
        FROM card_access_log cal
        JOIN access_card ac ON cal.cardId = ac.cardId
        JOIN person p ON ac.guestId = p.personId
        JOIN room r ON cal.roomId = r.roomID
        ORDER BY cal.accessTime DESC
        LIMIT {limit}
    """
    return run_query(sql)


def get_fixed_demo_answer(question: str):
    """
    Free Demo Mode:
    Route common hotel operations questions to fixed SQL skills.
    This does not call the OpenAI API, so it costs nothing.
    """
    q = question.lower().strip()

    if any(k in q for k in ["service", "revenue by service", "most revenue"]):
        sql = """
SELECT s.serviceType,
       ROUND(SUM(c.amount), 2) AS revenue
FROM charge c
JOIN service s ON c.serviceId = s.serviceId
GROUP BY s.serviceType
ORDER BY revenue DESC;
"""
        df = run_query(sql)
        insight = "Room-related charges are the largest revenue source, followed by event-related charges. This suggests that room occupancy and event usage are the main business drivers."
        intent = "Revenue Analytics"

    elif any(k in q for k in ["room status", "status breakdown", "room breakdown"]):
        sql = """
SELECT roomStatus,
       COUNT(*) AS count
FROM room
GROUP BY roomStatus
ORDER BY count DESC;
"""
        df = run_query(sql)
        insight = "Most rooms are currently available, while a smaller number are occupied, under cleaning, or under renovation. This helps operations staff understand room readiness."
        intent = "Room Operations"

    elif any(k in q for k in ["available room", "currently available", "which rooms are available"]):
        sql = """
SELECT r.roomID,
       r.roomNumber,
       r.baseRate,
       r.roomStatus,
       b.buildingName,
       w.wingName,
       f.floorNumber
FROM room r
JOIN floor f ON r.floorID = f.floorID
JOIN wing w ON f.wingID = w.wingID
JOIN building b ON w.buildingID = b.buildingID
WHERE r.roomStatus = 'available'
ORDER BY b.buildingName, w.wingName, f.floorNumber, r.roomNumber;
"""
        df = run_query(sql)
        insight = "These rooms are currently marked as available in the operational database. Front desk staff could use this view to support room assignment decisions."
        intent = "Room Availability"

    elif any(k in q for k in ["access", "card", "logs", "suspicious"]):
        sql = """
SELECT cal.logId,
       cal.cardId,
       p.first_name || ' ' || p.last_name AS guest,
       r.roomNumber,
       cal.accessTime,
       cal.direction
FROM card_access_log cal
JOIN access_card ac ON cal.cardId = ac.cardId
JOIN person p ON ac.guestId = p.personId
JOIN room r ON cal.roomId = r.roomID
ORDER BY cal.accessTime DESC
LIMIT 50;
"""
        df = run_query(sql)
        insight = "This view shows recent guest card access activity. It can support operational audits, guest service checks, and suspicious access investigations."
        intent = "Access Audit"

    elif any(k in q for k in ["billing", "billing party", "charges", "highest total charges"]):
        sql = """
SELECT bp.billingPartyId,
       COALESCE(p.first_name || ' ' || p.last_name, 'Organization ' || bp.organizationId) AS billingParty,
       ROUND(SUM(c.amount), 2) AS totalCharges,
       COUNT(c.chargeId) AS chargeCount
FROM billing_party bp
JOIN charge c ON bp.billingPartyId = c.billingPartyId
LEFT JOIN person p ON bp.personId = p.personId
GROUP BY bp.billingPartyId, billingParty
ORDER BY totalCharges DESC;
"""
        df = run_query(sql)
        insight = "This ranking identifies the billing parties responsible for the highest total charges. It can help the hotel prioritize billing review and payment follow-up."
        intent = "Billing Review"

    elif any(k in q for k in ["event usage", "event room", "events by room"]):
        sql = """
SELECT e.eventId,
       e.startDate,
       e.endDate,
       e.estimatedAttendance,
       r.roomNumber,
       er.usageSlot
FROM event e
JOIN event_room er ON e.eventId = er.eventId
JOIN room r ON er.roomId = r.roomID
ORDER BY e.startDate, e.eventId;
"""
        df = run_query(sql)
        insight = "This table shows how meeting or event spaces are used across events. It helps evaluate event room demand and scheduling patterns."
        intent = "Event Usage"

    elif any(k in q for k in ["attendance", "highest estimated attendance"]):
        sql = """
SELECT eventId,
       startDate,
       endDate,
       estimatedAttendance,
       estimatedGuestRooms
FROM event
ORDER BY estimatedAttendance DESC
LIMIT 10;
"""
        df = run_query(sql)
        insight = "These are the events with the highest expected attendance. Operations teams can use this to plan staffing, room allocation, and service preparation."
        intent = "Event Planning"

    elif any(k in q for k in ["near the pool", "pool"]):
        sql = """
SELECT r.roomID,
       r.roomNumber,
       r.roomStatus,
       r.baseRate,
       b.buildingName,
       w.wingName,
       w.proximityPool
FROM room r
JOIN floor f ON r.floorID = f.floorID
JOIN wing w ON f.wingID = w.wingID
JOIN building b ON w.buildingID = b.buildingID
WHERE w.proximityPool = 1
ORDER BY b.buildingName, w.wingName, r.roomNumber;
"""
        df = run_query(sql)
        insight = "These rooms are located in wings marked as close to the pool. This can support guest preference matching and room recommendation."
        intent = "Amenity-based Room Recommendation"

    elif any(k in q for k in ["guest stay", "stay history", "guests with multiple stays"]):
        sql = """
SELECT p.first_name || ' ' || p.last_name AS guest,
       COUNT(s.stayId) AS stayCount,
       MIN(s.checkIn) AS firstCheckIn,
       MAX(s.checkOut) AS latestCheckOut
FROM stay s
JOIN guest g ON s.guestId = g.guestId
JOIN person p ON g.guestId = p.personId
GROUP BY guest
ORDER BY stayCount DESC, latestCheckOut DESC;
"""
        df = run_query(sql)
        insight = "This view summarizes guest stay history. Guests with repeated stays may be valuable for loyalty or personalized service strategies."
        intent = "Guest Stay Analysis"

    elif any(k in q for k in ["top rooms", "room revenue", "rooms by revenue"]):
        sql = """
SELECT r.roomNumber,
       ROUND(SUM(c.amount), 2) AS totalRevenue,
       COUNT(c.chargeId) AS chargeCount
FROM charge c
JOIN room r ON c.roomId = r.roomID
GROUP BY r.roomNumber
ORDER BY totalRevenue DESC
LIMIT 10;
"""
        df = run_query(sql)
        insight = "This ranking shows which rooms are associated with the highest total charges. It can help identify high-value rooms or room categories."
        intent = "Room Revenue Analytics"

    else:
        return {
            "success": False,
            "mode": "Free Demo Mode",
            "intent": "Unsupported Demo Question",
            "sql": "",
            "qc_message": "This question is not covered by the free demo router. Try a supported hotel operations question or use LLM Agent Mode.",
            "dataframe": None,
            "analysis": "Free Demo Mode supports revenue, room status, room availability, access logs, billing, event usage, pool-proximity rooms, guest stay history, and room revenue questions."
        }

    return {
        "success": True,
        "mode": "Free Demo Mode",
        "intent": intent,
        "sql": sql.strip(),
        "qc_message": "Fixed SQL skill selected. Query is read-only and safe.",
        "dataframe": df,
        "analysis": insight
    }