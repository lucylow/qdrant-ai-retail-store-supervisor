## Vendor / Subprocessor Assessment — LiveMap (Draft)

This file tracks key subprocessors and infrastructure providers used by the LiveMap prototype. For production deployments, replace placeholders with your actual vendors and signed agreements.

| Vendor / Service | Region(s) | Data transferred? | Data types | DPA signed? | Security certifications | Retention / deletion notes |
|------------------|-----------|-------------------|-----------|------------|-------------------------|----------------------------|
| Cloud hosting (e.g. AWS, GCP, Azure) | TBD | Yes | application data, logs | TBD | e.g. ISO 27001, SOC 2 | Follow provider retention and deletion guarantees; ensure encrypted storage for any location data. |
| Qdrant (cloud or managed) | TBD | Yes | vector embeddings, pseudonymous identifiers | TBD | e.g. ISO 27001 (if applicable) | Confirm deletion guarantees for embeddings and logs; use hashed user IDs as payload keys. |
| Mapping provider (e.g. Mapbox, Google Maps) | TBD | Possibly | tile requests, approximate coordinates | TBD | Vendor‑specific | Ensure use of SDK in compliance with terms; avoid sending raw user identifiers. |
| LLM / model provider (e.g. OpenAI, Hugging Face Inference) | TBD | Possibly | prompts, intent text | TBD | Vendor‑specific | Prefer no‑training / no‑logging modes; avoid sending persistent identifiers where possible. |

For each vendor, record:

- **Contact and account owner**.
- **DPA / data processing terms** and signing status.
- **Regions and data residency** options.
- **Security whitepapers / certifications**.
- **Ability to delete or export data on request**.

