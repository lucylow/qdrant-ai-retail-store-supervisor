## LiveMap Privacy & Compliance — Assumptions (Prototype)

This document records explicit assumptions and limitations for the LiveMap prototype so reviewers and judges can quickly understand the scope.

- **Test data only**: the system is designed and configured for hackathon/demo use with synthetic or test users, not real customers.
- **No persistent location history**: LiveMap intents are ephemeral and automatically purged after a short TTL (5–15 minutes). There is no long‑term location history.
- **Coarse location by default**: matching and provider views use approximate (rounded) coordinates, not exact GPS points.
- **Exact coordinates optional and encrypted**: exact coordinates are only stored if a dedicated encryption key is configured and the user explicitly consents; otherwise they are never persisted.
- **Pseudonymous identifiers**: internal processing, logs and vector payloads use hashed user identifiers rather than raw IDs.
- **Limited operator access**: there is no general‑purpose admin UI for browsing individual location traces; debugging relies on pseudonymised logs.
- **Prototype legal review**: this repository includes draft DPIA and privacy policy documents, but they are not a substitute for production legal review.

