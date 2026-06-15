# Hotel Business Rules

## Room availability

A room is available only if its roomStatus is available and it does not have an overlapping room_reservation for the requested time window.

A reservation overlaps a requested time window if room_reservation.startDateTime is earlier than the requested end time and room_reservation.endDateTime is later than the requested start time.

## Sleeping rooms

Sleeping rooms have sleeping capacity, smoking status, toilet, TV, and phone attributes.

Sleeping rooms are usually allocated from check-in time to check-out time.

## Meeting rooms and events

Meeting rooms are scheduled by usage slots such as breakfast, morning, lunch, afternoon, supper, evening, and night.

Events may use one or more rooms through event_room.

Event questions usually require event, event_room, room, host, and person.

## Billing

Every charge should have a billingPartyId.

Charges may be associated with a stay, an event, a room, or a combination of these.

Revenue questions should use the charge table.

Service revenue questions should join charge with service.

Billing responsibility questions should join charge with billing_party, person, and organization.

## Access tracking

Guests use access cards to enter rooms.

Access tracking questions should use card_access_log, access_card, person, and room.

A suspicious access pattern may include access outside an assigned stay window or access to a room not assigned to the guest.
