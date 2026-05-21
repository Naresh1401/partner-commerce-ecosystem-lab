# AI-Assisted Engineering In Enterprise

How I would use Copilot-style tools safely:

- Ask AI to draft adapters, tests, and documentation, then review every contract boundary.
- Never paste secrets, customer data, payment data, or proprietary partner payloads into an unmanaged tool.
- Use AI to generate first-pass tests for edge cases such as invalid signatures, expired mandates, unknown SKUs, and rate limits.
- Require human review for auth, payment, webhook, and agent tool changes.
- Keep deterministic tests as the source of truth.

Example prompt:

```text
Generate pytest tests for a partner adapter that normalizes product, offer, inventory, and webhook payloads.
Include malformed payloads, missing fields, and decimal precision cases.
Do not invent production credentials.
```

