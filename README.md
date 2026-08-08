# UAE Visa Intel Client

A Python client for pulling live UAE government visa information (visa types,
requirements, fees, FAQs) via context.dev, scoped to official government
domains only (u.ae, icp.gov.ae, gdrfad.gov.ae, mofa.gov.ae).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your context.dev API key:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and paste your real key in place of `your_key_here`.

3. Run:
   ```bash
   python main.py
   ```

## Structure

```
uae-visa-agent/
├── .env.example          # copy to .env and add your key
├── requirements.txt
├── main.py                # entry point — runs sample queries
└── gov_intel/
    ├── __init__.py
    └── uae_visa_client.py # UAEVisaIntelClient — the actual context.dev integration
```

## What it does

`UAEVisaIntelClient` wraps context.dev's `/web/extract` endpoint, restricted
to four official UAE government sources:

- `u.ae` — federal information portal
- `icp.gov.ae` — Identity, Citizenship, Customs & Port Security Authority
- `gdrfad.gov.ae` — Dubai's residency & foreigners affairs authority
- `mofa.gov.ae` — Ministry of Foreign Affairs

Four methods are exposed:

| Method | Returns |
|---|---|
| `get_visa_types_overview()` | List of visa types from the federal portal |
| `get_visa_requirements(visa_type)` | Eligibility, documents, validity for a given visa |
| `get_visa_faqs(topic)` | Official Q&A content for a topic |
| `get_visa_fees(visa_type)` | Fee amounts in AED, with source section noted |

Responses are cached in-memory for 24 hours (visa rules don't change hourly),
and every extraction call passes explicit instructions telling context.dev
not to infer or estimate missing fields — important for anything fee- or
eligibility-related.

## Important

- Always surface the source URL next to any answer built from this client —
  don't present it as flat fact.
- If `ContextDevError` is raised, don't fall back to guessed/training-data
  info. Tell the user to check u.ae or ICP directly.
- Confirm exact endpoint paths/payload shape against current context.dev
  docs (https://context.dev/docs) — this follows the `/web/extract` naming
  from the hackathon brief, but exact field names may differ.

## Note on "Antigravity"

This is a plain Python project (stdlib + `requests` + `python-dotenv`), so it
should run in any environment that can execute `python main.py`, including
Google's Antigravity IDE. If Antigravity expects a specific manifest or
task-definition format instead of a plain script, let me know and I'll
restructure the entry point accordingly.
