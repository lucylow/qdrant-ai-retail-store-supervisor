## LiveMap — Location & Intent Sharing Privacy Policy (MVP)

LiveMap helps you discover nearby merchants who can fulfil your request in real time. This prototype is designed with privacy-by-default and privacy-by-design principles.

### What we collect

- **Intent text**: what you are looking for (for example, "haircut near Bahnhof at 16:00").
- **Approximate location**: a coarse version of your location (for example, neighbourhood or rounded coordinates).
- **Technical data**: basic telemetry needed to keep the service running (for example, request time, errors).

We do **not** share your name, email address, phone number or exact coordinates with merchants during the initial matching phase.

### How we use your data

- **Matching**: broadcast your intent and approximate location to nearby merchants so they can decide whether to respond.
- **Ranking**: score potential matches based on distance, suitability and availability.
- **Improvement**: aggregate, anonymised usage statistics to improve the service (optional, and without raw identifiers).

We only use your data for these purposes and do not sell your data.

### Location & retention

- **Coarse location only by default**: we store and use a coarse representation of your location for matching.
- **Short-lived intents**: LiveMap intents are ephemeral and expire automatically after a short period (typically 5–15 minutes).
- **Exact coordinates**: exact coordinates are only stored in encrypted form and only if you explicitly consent. They are only needed if/when you confirm a booking.

### Legal basis

For this prototype, our primary legal bases are:

- **Consent**: you explicitly opt in to broadcasting your approximate location and intent.
- **Contract**: where necessary to provide the service you requested (for example, completing a booking).

### Your choices & controls

- **Opt-in**: you choose whether to enable LiveMap broadcasting.
- **Opt-out at any time**: you can stop broadcasting and withdraw consent.
- **Delete my data**: you can request deletion of your LiveMap intents and associated embeddings. The system will remove them from the application store and from Qdrant where used.

### Vendors & infrastructure

LiveMap may rely on third‑party providers (for example Qdrant, cloud hosting, mapping providers, model providers) as subprocessors. We review their security posture, data protection commitments and retention policies before use. See `docs/vendor_assessment.md` for details.

### Prototype disclaimer

This repository implements a hackathon‑grade prototype of a privacy‑preserving LiveMap marketplace. It is **not** production legal advice. Before going live with real customer data you must:

- perform a full Data Protection Impact Assessment (see `docs/DPIA.md`),
- review and update this policy with your legal team, and
- sign appropriate Data Processing Agreements with all subprocessors.

