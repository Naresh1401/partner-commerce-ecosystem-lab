# Partner Commerce Ecosystem Lab

Portfolio repo for the JD nice-to-have skills:

- Major partner ecosystems and third-party commerce platforms
- Google UCP / Universal Commerce Protocol concepts
- AP2-style agentic payment authorization concepts
- AI-assisted engineering practices in enterprise environments

The project shows how to normalize different partner payloads into one internal commerce contract without brittle point-to-point integrations.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn partner_commerce.main:app --reload --app-dir src
```

## What This Demonstrates

- Adapter pattern for Shopify-like, marketplace-like, and UCP-like partner payloads
- Partner onboarding checklist
- HMAC webhook verification
- AP2-inspired checkout mandate validation
- AI-assisted engineering guardrails and prompt templates

## Useful Endpoints

- `GET /health`
- `GET /v1/partners`
- `POST /v1/partners/{partner_id}/normalize`
- `POST /v1/mandates/validate`
- `POST /v1/webhooks/{partner_id}`

