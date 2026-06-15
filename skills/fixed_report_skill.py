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
    return run_query("""
        SELECT s.serviceType, ROUND(SUM(c.amount), 2) AS revenue
        FROM charge c
        JOIN service s ON c.serviceId = s.serviceId
        GROUP BY s.serviceType
        ORDER BY revenue DESC
    """)


def room_status_summary():
    return run_query("""
        SELECT roomStatus, COUNT(*) AS count
        FROM room
        GROUP BY roomStatus
        ORDER BY count DESC
    """)


def recent_access_logs(limit=30):
    return run_query(f"""
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
    """)
