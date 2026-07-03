#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

ROOT = Path(__file__).parent
BOT_URL = "http://127.0.0.1:8080"


def call(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = request.Request(
        f"{BOT_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def push(scope: str, context_id: str, payload: dict) -> dict:
    return call(
        "POST",
        "/v1/context",
        {
            "scope": scope,
            "context_id": context_id,
            "version": 1,
            "payload": payload,
            "delivered_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def main() -> None:
    call("POST", "/v1/teardown", {})

    category = json.loads((ROOT / "dataset/categories/dentists.json").read_text())
    merchants = json.loads((ROOT / "dataset/merchants_seed.json").read_text())["merchants"]
    triggers = json.loads((ROOT / "dataset/triggers_seed.json").read_text())["triggers"]
    customers = json.loads((ROOT / "dataset/customers_seed.json").read_text())["customers"]

    merchant = next(item for item in merchants if item["merchant_id"] == "m_001_drmeera_dentist_delhi")
    trigger = next(item for item in triggers if item["id"] == "trg_001_research_digest_dentists")
    customer = next(item for item in customers if item["customer_id"] == "c_001_priya_for_m001")
    recall = next(item for item in triggers if item["id"] == "trg_003_recall_due_priya")

    print("healthz:", call("GET", "/v1/healthz"))
    print("category:", push("category", category["slug"], category))
    print("merchant:", push("merchant", merchant["merchant_id"], merchant))
    print("customer:", push("customer", customer["customer_id"], customer))
    print("trigger:", push("trigger", trigger["id"], trigger))
    print("recall:", push("trigger", recall["id"], recall))

    tick = call(
        "POST",
        "/v1/tick",
        {
            "now": "2026-04-26T10:35:00Z",
            "available_triggers": [trigger["id"], recall["id"]],
        },
    )
    print("tick actions:", json.dumps(tick, ensure_ascii=False, indent=2))

    reply = call(
        "POST",
        "/v1/reply",
        {
            "conversation_id": tick["actions"][0]["conversation_id"],
            "merchant_id": merchant["merchant_id"],
            "customer_id": None,
            "from_role": "merchant",
            "message": "Yes please send the abstract. Also draft the patient WhatsApp.",
            "received_at": "2026-04-26T10:42:00Z",
            "turn_number": 2,
        },
    )
    print("reply:", json.dumps(reply, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
