# KPI Definitions

Total Revenue = SUM(charge.amount)

Revenue by Service Type = SUM(charge.amount) grouped by service.serviceType

Room Revenue = SUM(charge.amount) where serviceType is room

Event Revenue = SUM(charge.amount) where serviceType is event

Available Room Count = COUNT(room) where roomStatus = 'available'

Room Status Breakdown = COUNT(room) grouped by roomStatus

Top Revenue Rooms = SUM(charge.amount) grouped by room.roomNumber

Event Utilization = COUNT(event_room records) grouped by usageSlot or room

Repeat Guests = guests with more than one stay
