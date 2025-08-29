# SOP — FDA Warning Letters ETL (v0.1)
Effective: 2025-08-29

Purpose: Ingest Warning Letters, extract CFR codes, apply QA, persist, and serve via API.
Procedure: Fetch → Parse (regex) → Validate → De-dup → Persist → QA → Publish endpoints.
Records: URL, fetched timestamp, SHA256 of raw text.
