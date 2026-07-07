# Research Architecture Notes

This folder documents the architecture decisions that keep the protocol implementation aligned with the roadmap.

## Current Decisions

- Identity is the primary trust anchor, not a single device
- Business logic belongs in Django, not in the UI
- Clients should stay thin and use the backend APIs
- Biometrics are a research track and must remain abstracted from the core protocol
- Persistent data belongs in PostgreSQL

## Open Areas

- Key lifecycle and sealed storage
- Pairing session lifetime and revocation
- Challenge-response hardening
- Device trust and recovery workflows
- Future audit database separation
