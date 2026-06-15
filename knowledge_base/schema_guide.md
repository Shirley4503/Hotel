# HotelMind Schema Guide

## Core location tables

building stores hotel buildings. Key fields include buildingID and buildingName.

wing stores wings inside buildings. It includes wingID, buildingID, wingName, proximityPool, proximityParking, and handicappedAccess.

floor stores floors inside wings. It includes floorID, wingID, floorNumber, and smokingDesignation.

room stores all physical rooms and facilities. It includes roomID, floorID, roomNumber, baseRate, and roomStatus.

## Room capability tables

sleeping_room_details stores sleeping room features such as capacity, smoking, hasToilet, hasTV, and hasPhone.

meeting_room_details stores meeting room capacity through seatingCapacity.

suite_details links suite rooms to sleeping and meeting room components.

room_bed links rooms to bed types and quantities.

room_adjacency stores adjacent room relationships and whether a private door exists.

## Reservation and stay tables

reservation stores reservation-level information including billingPartyId, reservationDate, depositRequired, and estimatedGuests.

room_reservation maps reservations to rooms and reserved time windows.

stay stores actual guest stays, including guestId, checkIn, and checkOut.

room_assignment maps actual stays to assigned rooms and assignment windows.

## Guest and billing tables

person stores names and contact information.

guest identifies people who are hotel guests.

host identifies people who host events.

organization stores organizations that may be responsible for billing.

billing_party identifies the responsible party for charges. A billing party can be a person, an organization, or both depending on the record.

## Event tables

event stores event-level information, including hostId, startDate, endDate, estimatedAttendance, and estimatedGuestRooms.

event_room maps events to rooms and usage slots such as morning, lunch, afternoon, evening, and night.

## Charges and services

service stores service categories, such as room, event, food, spa, parking, laundry, internet, and phone.

charge stores billed transactions. It includes serviceId, billingPartyId, roomId, stayId, eventId, amount, chargeDateTime, and description.

Use charge.amount for revenue questions.

## Access tracking

access_card maps guest cards to guests.

card_access_log records card usage. It includes cardId, roomId, accessTime, and direction.

Use card_access_log with access_card, person, and room to answer access tracking questions.
