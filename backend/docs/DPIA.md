## LiveMap Data Protection Impact Assessment (DPIA) — Draft

### 1. Overview

- **System**: LiveMap real‑time retail intent and location matching.
- **Controller**: Hackathon project team (replace with organisation name for production).
- **Purpose**: Allow shoppers to broadcast short‑lived service requests (intents) and discover nearby merchants able to fulfil them.
- **Data subjects**: Shoppers and merchants using the LiveMap feature.

### 2. Processing description

- **Data collected**:
  - pseudonymised user identifier,
  - free‑text intent description,
  - approximate (coarse) location,
  - optional encrypted exact coordinates (only on explicit consent),
  - basic technical metadata (timestamps, request IDs, logs).
- **Operations**:
  - creation and short‑term storage of intents,
  - semantic and geo‑spatial matching against nearby merchants using Qdrant,
  - optional aggregation for analytics.
- **Retention**:
  - intents are ephemeral and automatically expire after 5–15 minutes,
  - logs and analytics are pseudonymised and aggregated where possible.

### 3. Legal basis & necessity

- **Legal bases**:
  - explicit consent for broadcasting location and intent,
  - contract where matching is necessary to deliver the requested service.
- **Necessity & proportionality**:
  - only coarse location is used for initial matching,
  - identifiers are pseudonymised,
  - intents are time‑limited and automatically purged,
  - deletion and opt‑out controls are exposed via API and UI.

### 4. Risks to data subjects

- Re‑identification risk if coarse location, intent text and timing are combined with external data.
- Unauthorised access to location history or exact coordinates.
- Misuse of intent data by merchants (for example, profiling, harassment, competition issues).
- Cross‑border transfers to subprocessors without adequate safeguards.

### 5. Mitigations

- **Data minimisation**: store only pseudonymous identifiers and coarse location for matching; exact coordinates are encrypted and only used post‑booking.
- **Ephemeral storage**: TTL‑based deletion of intents and associated embeddings.
- **Access control**: restrict operator access to production data; log access to any exact coordinate fields.
- **Vendor due diligence**: maintain `docs/vendor_assessment.md` for each subprocessor and sign DPAs where applicable.
- **User controls**: provide “stop sharing” and “delete my data” actions; expose `/livemap/user/{user_id_hash}/delete` API.
- **Security**: encryption in transit (TLS), encryption at rest for storage that may hold coordinates, and regular security testing.

### 6. Residual risk & conclusion

After applying the above mitigations, residual risk is reduced but not eliminated (particularly around potential re‑identification in dense telemetry or merchant misuse). For a production launch, this DPIA should be:

- formally reviewed by a Data Protection Officer or privacy counsel,
- updated with real deployment details (regions, vendors, retention),
- revisited whenever LiveMap functionality or data flows materially change.

