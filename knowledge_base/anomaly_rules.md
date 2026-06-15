# Anomaly Rules

## SQL safety

The AI agent should only generate SELECT queries.

The AI agent must not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, TRUNCATE, PRAGMA, VACUUM, ATTACH, or DETACH.

## Billing anomalies

A billing anomaly may occur if a charge has no billingPartyId.

A billing anomaly may occur if amount is less than or equal to zero.

A charge should ideally be linked to a stay, an event, a room, or a responsible billing party.

## Access anomalies

An access anomaly may occur if a card access record occurs outside the guest's assigned stay window.

An access anomaly may occur if a guest accesses a room that is not assigned to their stay.

## Room assignment anomalies

A room assignment conflict may occur when two stays overlap for the same room.

A room should not be assigned if roomStatus is maintenance, renovation, or cleaning.
