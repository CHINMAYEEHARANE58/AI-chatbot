# magicpin Vera Challenge Bot

This workspace contains a complete local Vera prototype:

- `bot.py` — stateful HTTP backend for the magicpin judge API
- `frontend/` — Vera merchant dashboard served by the backend
- `smoke_test.py` — dependency-free local API smoke test
- `dataset/`, `examples/`, and challenge briefs — source data and evaluation contract

## Start Frontend + Backend

Run one server for both the dashboard and API:

```bash
python3 bot.py --host 127.0.0.1 --port 8080
```

Open the dashboard:

```text
http://127.0.0.1:8080/
```

When the dashboard opens it calls `/v1/demo/bootstrap` automatically, loading the bundled datasets into the backend. Use:

- `+` button: simulate an active trigger and send a Vera-composed message into the chat
- `V` button: generate a backend-composed Vera draft into the composer
- Composer text box: type as the merchant; Vera replies through `/v1/demo/reply`

Judge/API endpoints:

```text
GET  /v1/healthz
GET  /v1/metadata
POST /v1/context
POST /v1/tick
POST /v1/reply
POST /v1/teardown
```

## Validate Locally

With `bot.py` running:

```bash
python3 smoke_test.py
```

The official `judge_simulator.py` also works, but it requires an LLM API key in its configuration before it starts.

## Is This Using An LLM?

The local bot uses a deterministic rule-based composer built from the challenge contexts, so it works without any external API key and does not leak merchant/customer data. The official judge still uses an LLM to score your responses. To use the official simulator, add an LLM API key in `judge_simulator.py`.
