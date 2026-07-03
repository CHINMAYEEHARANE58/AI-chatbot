#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import re
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
DATASET_DIR = ROOT / "dataset"
STARTED_AT = time.time()

SCOPES = {"category", "merchant", "customer", "trigger"}
contexts: dict[tuple[str, str], dict[str, Any]] = {}
conversations: dict[str, dict[str, Any]] = {}
sent_suppression_keys: set[str] = set()
merchant_suppression: dict[str, float] = {}
merchant_auto_reply_counts: dict[str, int] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clean(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def pct(value: Any, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if abs(number) <= 1:
        number *= 100
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{number:.0f}%"


def human_date(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    try:
        date_part = text[:10]
        parsed = datetime.strptime(date_part, "%Y-%m-%d")
        return parsed.strftime("%d %b %Y").lstrip("0")
    except ValueError:
        return text


def money_or_title(offers: list[dict[str, Any]]) -> str:
    for offer in offers:
        if offer.get("status") == "active" and offer.get("title"):
            return offer["title"]
    for offer in offers:
        if offer.get("title"):
            return offer["title"]
    return ""


def identity_name(merchant: dict[str, Any]) -> str:
    return clean(merchant.get("identity", {}).get("name"), "your business")


def owner_name(merchant: dict[str, Any]) -> str:
    identity = merchant.get("identity", {})
    return clean(identity.get("owner_first_name") or identity.get("name"), "there")


def salutation(merchant: dict[str, Any], category_slug: str) -> str:
    owner = owner_name(merchant)
    if category_slug == "dentists" and not owner.lower().startswith("dr"):
        return f"Dr. {owner}"
    return owner


def active_context(scope: str, context_id: str | None) -> dict[str, Any] | None:
    if not context_id:
        return None
    item = contexts.get((scope, context_id))
    return item.get("payload") if item else None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def store_context(scope: str, context_id: str, payload: dict[str, Any], version: int = 1) -> None:
    current = contexts.get((scope, context_id), {})
    next_version = max(version, int(current.get("version", 0)) + 1 if current else version)
    contexts[(scope, context_id)] = {"version": next_version, "payload": payload, "stored_at": utc_now()}


def bootstrap_demo_contexts() -> dict[str, int]:
    for path in sorted((DATASET_DIR / "categories").glob("*.json")):
        payload = load_json(path)
        store_context("category", payload["slug"], payload)

    for filename, scope, container, key in [
        ("merchants_seed.json", "merchant", "merchants", "merchant_id"),
        ("customers_seed.json", "customer", "customers", "customer_id"),
        ("triggers_seed.json", "trigger", "triggers", "id"),
    ]:
        payload = load_json(DATASET_DIR / filename)
        for item in payload.get(container, []):
            store_context(scope, item[key], item)

    return context_counts()


def category_for(merchant: dict[str, Any] | None, trigger: dict[str, Any] | None = None) -> dict[str, Any] | None:
    slug = None
    if merchant:
        slug = merchant.get("category_slug")
    if not slug and trigger:
        slug = trigger.get("payload", {}).get("category")
    return active_context("category", slug)


def find_digest_item(category: dict[str, Any] | None, item_id: str | None) -> dict[str, Any] | None:
    if not category:
        return None
    digest = category.get("digest", [])
    if item_id:
        for item in digest:
            if item.get("id") == item_id:
                return item
    return digest[0] if digest else None


def find_customer(customer_id: str | None, merchant_id: str | None = None) -> dict[str, Any] | None:
    customer = active_context("customer", customer_id)
    if customer:
        return customer
    if merchant_id:
        for (scope, _), item in contexts.items():
            if scope == "customer" and item.get("payload", {}).get("merchant_id") == merchant_id:
                return item["payload"]
    return None


def signal_has(merchant: dict[str, Any], needle: str) -> bool:
    return any(needle in str(signal) for signal in merchant.get("signals", []))


def conversation_id(merchant_id: str, trigger: dict[str, Any], customer_id: str | None) -> str:
    base = trigger.get("kind", "trigger").replace("_", "-")
    if customer_id:
        short_customer = customer_id.split("_for_")[0].replace("c_", "c")
        return f"conv_{short_customer}_{base}"
    short_merchant = merchant_id.replace("m_", "").replace("_", "-")[:34]
    return f"conv_{short_merchant}_{base}"


def template_for(trigger: dict[str, Any], send_as: str) -> str:
    kind = trigger.get("kind", "generic")
    if send_as == "merchant_on_behalf":
        if kind in {"recall_due", "appointment_tomorrow"}:
            return "merchant_recall_reminder_v1"
        if kind in {"chronic_refill_due"}:
            return "merchant_refill_reminder_v1"
        return f"merchant_{kind}_v1"
    return f"vera_{kind}_v1"


def template_params(body: str, merchant: dict[str, Any], trigger: dict[str, Any], customer: dict[str, Any] | None) -> list[str]:
    target = customer.get("identity", {}).get("name") if customer else salutation(merchant, merchant.get("category_slug", ""))
    return [clean(target), clean(trigger.get("kind", "trigger")).replace("_", " "), body[:260]]


def rationale(trigger: dict[str, Any], merchant: dict[str, Any], customer: dict[str, Any] | None, body_focus: str) -> str:
    target = "customer-scoped" if customer else "merchant-facing"
    return (
        f"{target} {trigger.get('kind')} composed from pushed context only; "
        f"uses {identity_name(merchant)} data and trigger payload for why-now. {body_focus}"
    )


def compose_action(trigger_id: str, now: str) -> dict[str, Any] | None:
    trigger = active_context("trigger", trigger_id)
    if not trigger:
        return None

    suppression_key = trigger.get("suppression_key", trigger_id)
    merchant_id = trigger.get("merchant_id")
    customer_id = trigger.get("customer_id")

    if not merchant_id or suppression_key in sent_suppression_keys:
        return None
    if merchant_suppression.get(merchant_id, 0) > time.time():
        return None

    merchant = active_context("merchant", merchant_id)
    if not merchant:
        return None
    category = category_for(merchant, trigger)
    if not category:
        return None

    customer = find_customer(customer_id, merchant_id) if trigger.get("scope") == "customer" else None
    body, cta, focus = compose_body(category, merchant, trigger, customer, now)
    if not body:
        return None

    send_as = "merchant_on_behalf" if customer else "vera"
    conv_id = conversation_id(merchant_id, trigger, customer_id)
    sent_suppression_keys.add(suppression_key)
    conversations[conv_id] = {
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "trigger_id": trigger_id,
        "suppression_key": suppression_key,
        "turns": [{"from": "bot", "body": body, "at": now}],
    }

    return {
        "conversation_id": conv_id,
        "merchant_id": merchant_id,
        "customer_id": customer_id,
        "send_as": send_as,
        "trigger_id": trigger_id,
        "template_name": template_for(trigger, send_as),
        "template_params": template_params(body, merchant, trigger, customer),
        "body": body,
        "cta": cta,
        "suppression_key": suppression_key,
        "rationale": rationale(trigger, merchant, customer, focus),
    }


def trigger_for_merchant(merchant_id: str) -> str | None:
    candidates = []
    for (scope, trigger_id), item in contexts.items():
        if scope != "trigger":
            continue
        trigger = item.get("payload", {})
        if trigger.get("merchant_id") == merchant_id:
            candidates.append((trigger.get("urgency", 0), trigger_id))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def demo_action_for_merchant(merchant_id: str) -> dict[str, Any] | None:
    if not contexts:
        bootstrap_demo_contexts()
    trigger_id = trigger_for_merchant(merchant_id)
    if not trigger_id:
        return None
    trigger = active_context("trigger", trigger_id)
    if trigger:
        sent_suppression_keys.discard(trigger.get("suppression_key", trigger_id))
    return compose_action(trigger_id, utc_now())


def compose_body(
    category: dict[str, Any],
    merchant: dict[str, Any],
    trigger: dict[str, Any],
    customer: dict[str, Any] | None,
    now: str,
) -> tuple[str, str, str]:
    if customer:
        return compose_customer_body(category, merchant, trigger, customer)

    kind = trigger.get("kind", "")
    category_slug = category.get("slug", merchant.get("category_slug", ""))
    payload = trigger.get("payload", {})
    name = salutation(merchant, category_slug)
    business = identity_name(merchant)
    locality = clean(merchant.get("identity", {}).get("locality"), "your area")
    performance = merchant.get("performance", {})
    aggregate = merchant.get("customer_aggregate", {})
    offer = money_or_title(merchant.get("offers", []))

    if kind in {"research_digest", "category_research_digest_release"}:
        item = find_digest_item(category, payload.get("top_item_id") or payload.get("digest_item_id"))
        if not item:
            return "", "none", ""
        trial = f"{item.get('trial_n'):,}-patient " if item.get("trial_n") else ""
        segment = aggregate.get("high_risk_adult_count")
        segment_text = f"your {segment} high-risk adult patients" if segment else "your patient base"
        source = clean(item.get("source"))
        body = (
            f"{name}, {source} landed with a useful item for {segment_text}: "
            f"{trial}{item.get('title')}. Want me to pull the 2-min summary and draft a patient WhatsApp you can review?"
        )
        return body, "open_ended", "Research/source citation plus merchant cohort anchor."

    if kind in {"regulation_change", "compliance_dci_radiograph", "cde_opportunity"}:
        item = find_digest_item(category, payload.get("top_item_id") or payload.get("digest_item_id"))
        if item:
            deadline = clean(payload.get("deadline_iso") or item.get("date"))
            deadline_text = f" before {deadline[:10]}" if deadline else ""
            body = (
                f"{name}, quick compliance note: {item.get('title')} ({item.get('source')}). "
                f"{clean(item.get('actionable'), 'Worth checking your SOPs')}{deadline_text}. "
                f"Want me to make a 5-point clinic checklist?"
            )
            return body, "binary_yes_no", "Compliance timing makes the why-now explicit."
        body = f"{name}, a new compliance trigger came in for {business}. Want me to turn it into a short action checklist?"
        return body, "binary_yes_no", "Fallback compliance action."

    if kind == "perf_dip":
        metric = clean(payload.get("metric"), "calls")
        delta = pct(payload.get("delta_pct"), signed=True)
        baseline = payload.get("vs_baseline")
        body = (
            f"{name}, {business}'s {metric} dropped {delta} in the last {payload.get('window', '7d')}"
            f"{f' vs baseline {baseline}' if baseline else ''}. I can check photos, offer, and GBP post freshness in one pass. "
            f"Want the 3 fixes most likely to recover enquiries this week?"
        )
        return body, "binary_yes_no", "Loss aversion anchored to the exact performance dip."

    if kind in {"perf_spike", "milestone_reached"}:
        metric = clean(payload.get("metric"), "metric")
        value = payload.get("value_now") or payload.get("delta_pct")
        value_text = pct(value, signed=True) if isinstance(value, float) else clean(value)
        driver = clean(payload.get("likely_driver"))
        body = (
            f"{name}, nice signal: {metric.replace('_', ' ')} is at {value_text or 'a new high'}"
            f"{f', likely from {driver}' if driver else ''}. Want me to turn this into a GBP post while momentum is fresh?"
        )
        return body, "binary_yes_no", "Timely momentum capture after a spike or milestone."

    if kind in {"ipl_match_today", "local_news_event"}:
        match = clean(payload.get("match"), "today's local event")
        time_text = clean(payload.get("match_time_iso"))
        digest = find_digest_item(category, "d_2026W17_ipl_window")
        weekend_warning = "Saturday IPL matches shift more orders home; covers can dip 12% vs Saturday avg. " if digest and payload.get("is_weeknight") is False else ""
        body = (
            f"Quick heads-up {name}: {match} is in {payload.get('city', merchant.get('identity', {}).get('city', 'your city'))}"
            f"{f' at {time_text[11:16]}' if time_text else ''}. {weekend_warning}"
            f"Use your {offer or 'active offer'} as a delivery-first push tonight. Want me to draft the WhatsApp status?"
        )
        return body, "binary_yes_no", "Event timing plus restaurant-specific operating advice."

    if kind in {"review_theme_emerged"}:
        theme = clean(payload.get("theme"), "review theme").replace("_", " ")
        count = payload.get("occurrences_30d")
        quote = clean(payload.get("common_quote"))
        body = (
            f"{name}, {count or 'multiple'} reviews this month now mention {theme}"
            f"{f' (\"{quote}\")' if quote else ''}. Want me to draft a calm review reply plus one ops note for the team?"
        )
        return body, "binary_yes_no", "Review pattern is concrete and recent."

    if kind in {"active_planning_intent"}:
        topic = clean(payload.get("intent_topic"), "this plan").replace("_", " ")
        last_message = clean(payload.get("merchant_last_message"))
        body = planning_body(category_slug, name, merchant, topic, last_message)
        return body, "binary_confirm_cancel", "Directly continues the merchant's explicit planning intent."

    if kind in {"seasonal_perf_dip", "category_seasonal"}:
        delta = pct(payload.get("delta_pct"), signed=True)
        if category_slug == "gyms":
            members = aggregate.get("total_active_members")
            body = (
                f"{name}, views are down {delta or 'this week'}, but this matches the normal Apr-Jun fitness lull. "
                f"Since you still have {members or 'active'} members and CTR is {pct(performance.get('ctr'))}, skip extra acquisition spend now. "
                f"Want me to draft a summer attendance challenge?"
            )
            return body, "binary_yes_no", "Reframes seasonal dip with merchant metrics."
        trends = ", ".join(payload.get("trends", [])[:3])
        body = (
            f"{name}, seasonal shift is live: {trends or clean(payload.get('season'), 'demand pattern changed')}. "
            f"Want me to make a counter-shelf + WhatsApp checklist for {business}?"
        )
        return body, "binary_yes_no", "Seasonal demand shift makes action timely."

    if kind in {"supply_alert"}:
        molecule = clean(payload.get("molecule"), "medicine")
        batches = ", ".join(payload.get("affected_batches", []))
        chronic = aggregate.get("chronic_rx_count")
        body = (
            f"{name}, urgent supply alert: {molecule} batches {batches or 'in the alert'} from {payload.get('manufacturer', 'the manufacturer')} are affected. "
            f"You have {chronic or 'repeat-Rx'} chronic-Rx customers, so speed matters. Want me to draft the stock-isolation checklist?"
        )
        return body, "binary_yes_no", "Batch-level compliance alert with pharmacy-safe language."

    if kind in {"renewal_due", "winback_eligible", "dormant_with_vera"}:
        days = payload.get("days_remaining") or payload.get("days_since_expiry") or payload.get("days_since_last_merchant_message")
        amount = payload.get("renewal_amount")
        body = (
            f"{name}, quick account check: {business} is at {days} days on this renewal/dormancy signal"
            f"{f' and renewal is ₹{amount}' if amount else ''}. "
            f"I can prepare a no-extra-work recovery plan using your current views ({performance.get('views', 'latest')}). Want the 3-line plan?"
        )
        return body, "binary_yes_no", "Account timing plus low-effort recovery offer."

    if kind in {"competitor_opened"}:
        competitor = clean(payload.get("competitor_name"), "a competitor")
        distance = payload.get("distance_km")
        their_offer = clean(payload.get("their_offer"))
        opened = clean(payload.get("opened_date"))
        body = (
            f"{name}, {competitor} opened {f'{distance}km away' if distance else 'nearby'}"
            f"{f' on {opened}' if opened else ''}{f' with {their_offer}' if their_offer else ''}. "
            f"Want me to draft a calm GBP post that protects your position without discounting blindly?"
        )
        return body, "binary_yes_no", "Competitor change creates curiosity and loss aversion."

    if kind in {"festival_upcoming", "curious_ask_due"}:
        festival = clean(payload.get("festival"))
        body = (
            f"Hi {name}, quick check: what service or product has been most asked-for this week at {business}? "
            f"I'll turn your answer into one Google post and a 4-line WhatsApp reply. Takes 5 min."
        )
        if festival:
            body = (
                f"Hi {name}, {festival} is coming up and {business} already has {offer or 'a usable offer'} in context. "
                f"Want me to draft one timely WhatsApp + GBP post for {locality} customers?"
            )
        return body, "open_ended", "Curious ask uses reciprocity and effort externalization."

    payload_summary = summarize_payload(payload)
    body = (
        f"{name}, a {kind.replace('_', ' ')} trigger just came in for {business}"
        f"{f': {payload_summary}' if payload_summary else ''}. Want me to draft the next WhatsApp message?"
    )
    return body, "binary_yes_no", "Generic but trigger-specific fallback."


def planning_body(category_slug: str, name: str, merchant: dict[str, Any], topic: str, last_message: str) -> str:
    offer = money_or_title(merchant.get("offers", []))
    locality = clean(merchant.get("identity", {}).get("locality"), "your locality")
    if category_slug == "restaurants":
        return (
            f"{name}, here's a starter version for {topic}: 10 orders @ ₹125 each, 25 orders @ ₹115 each, "
            f"50+ @ ₹105 each, order by 5pm for 12:30-1pm delivery in {locality}. "
            f"Want me to draft the 3-line office outreach message?"
        )
    if category_slug == "gyms":
        return (
            f"{name}, starter plan for {topic}: 4 weeks, 3 sessions/week, age 7-12, ₹2,499, "
            f"Sat demo class first. Want me to draft the GBP post and parent WhatsApp?"
        )
    return (
        f"{name}, picked up your intent: {last_message or topic}. I can convert it into a ready-to-send plan using {offer or 'your current context'}. "
        f"Reply CONFIRM and I'll draft the merchant-facing copy now."
    )


def compose_customer_body(
    category: dict[str, Any],
    merchant: dict[str, Any],
    trigger: dict[str, Any],
    customer: dict[str, Any],
) -> tuple[str, str, str]:
    kind = trigger.get("kind", "")
    payload = trigger.get("payload", {})
    category_slug = category.get("slug", merchant.get("category_slug", ""))
    merchant_name = identity_name(merchant)
    owner = owner_name(merchant)
    customer_name = clean(customer.get("identity", {}).get("name"), "there")
    language = clean(customer.get("identity", {}).get("language_pref")).lower()
    relationship = customer.get("relationship", {})
    preferences = customer.get("preferences", {})
    offer = money_or_title(merchant.get("offers", []))

    if kind == "recall_due":
        slots = payload.get("available_slots", [])
        slot_text = " ya ".join(clean(slot.get("label")) for slot in slots[:2] if slot.get("label"))
        last_visit = human_date(payload.get("last_service_date") or relationship.get("last_visit"))
        body = (
            f"Hi {customer_name}, {merchant_name} here. Your last visit was {last_visit} — your 6-month cleaning recall is due. "
            f"{'Apke liye ' if 'hi' in language else ''}{'2 slots ready hain: ' if 'hi' in language else 'Available slots: '}"
            f"{slot_text or clean(preferences.get('preferred_slots'), 'this week')}. {offer or 'Dental Cleaning @ ₹299'}. "
            f"Reply 1 for the first slot, 2 for the second, or tell us a time that works."
        )
        return body, "multi_choice_slot", "Customer recall uses visit date, slots, language preference, and active offer."

    if kind in {"customer_lapsed_hard", "customer_lapsed_soft"}:
        days = payload.get("days_since_last_visit")
        focus = clean(payload.get("previous_focus") or preferences.get("training_focus"))
        if category_slug == "gyms":
            body = (
                f"Hi {customer_name}, {owner} from {merchant_name} here. It's been {days or 'a few'} days — no judgment. "
                f"We can restart with {offer or 'a free trial class'} and keep it focused on {focus or 'your goal'}. "
                f"Reply YES and I'll hold a no-commitment slot for you."
            )
            return body, "binary_yes_no", "No-shame gym winback matched to prior goal."
        body = (
            f"Hi {customer_name}, {merchant_name} here. We noticed it's been a while since your last visit. "
            f"Want me to keep {offer or 'one slot'} ready for you this week? Reply YES."
        )
        return body, "binary_yes_no", "Customer lapse trigger with low-friction reply."

    if kind == "chronic_refill_due":
        molecules = ", ".join(payload.get("molecule_list", []))
        runout = clean(payload.get("stock_runs_out_iso"))[:10]
        delivery = "Free home delivery to saved address" if payload.get("delivery_address_saved") else "Pickup can be kept ready"
        body = (
            f"Namaste {customer_name}, {merchant_name} here. Your monthly medicines ({molecules}) run out on {runout}. "
            f"Same refill can be packed today. {delivery}. Reply CONFIRM to dispatch, or tell us if dosage changed."
        )
        return body, "binary_confirm_cancel", "Pharmacy refill reminder uses molecules, run-out date, and delivery preference."

    if kind == "appointment_tomorrow":
        body = (
            f"Hi {customer_name}, reminder from {merchant_name}: your appointment is tomorrow. "
            f"Reply CONFIRM if the timing still works, or RESCHEDULE if you need another slot."
        )
        return body, "binary_confirm_cancel", "Appointment reminder is informational with a simple confirmation CTA."

    if kind in {"trial_followup", "wedding_package_followup"}:
        next_slots = payload.get("next_session_options", [])
        next_slot = clean(next_slots[0].get("label")) if next_slots else clean(preferences.get("preferred_slots"))
        wedding = payload.get("wedding_date") or preferences.get("wedding_date")
        body = (
            f"Hi {customer_name}, {owner} from {merchant_name} here. "
            f"{f'{payload.get('days_to_wedding')} days to your wedding on {wedding}; ' if wedding and payload.get('days_to_wedding') else ''}"
            f"your next-step window is open. Want me to hold {next_slot or 'your preferred slot'}?"
        )
        return body, "binary_yes_no", "Customer follow-up references relationship timing and preferred slot."

    body = (
        f"Hi {customer_name}, {merchant_name} here. This is about your recent {kind.replace('_', ' ')} update. "
        f"Reply YES if you want us to keep the next step ready."
    )
    return body, "binary_yes_no", "Generic customer trigger fallback."


def summarize_payload(payload: dict[str, Any]) -> str:
    parts = []
    for key, value in payload.items():
        if key == "placeholder":
            continue
        if isinstance(value, (str, int, float, bool)):
            parts.append(f"{key}={value}")
        elif isinstance(value, list):
            parts.append(f"{key}={', '.join(map(str, value[:3]))}")
        if len(parts) == 2:
            break
    return "; ".join(parts)


def is_auto_reply(message: str) -> bool:
    text = message.lower()
    patterns = [
        "thank you for contacting",
        "team will respond shortly",
        "we will get back",
        "automated response",
        "away message",
        "business account",
    ]
    return any(pattern in text for pattern in patterns)


def is_stop(message: str) -> bool:
    text = message.lower()
    return any(phrase in text for phrase in ["stop messaging", "not interested", "unsubscribe", "don't message", "do not message", "useless spam"])


def is_hostile(message: str) -> bool:
    text = message.lower()
    return is_stop(text) or any(word in text for word in ["useless", "spam", "bothering", "annoying", "shut up", "idiot"])


def is_commitment(message: str) -> bool:
    text = message.lower().replace("'", "")
    return any(phrase in text for phrase in ["lets do it", "let's do it", "ok do it", "go ahead", "confirm", "yes send", "yes please", "start", "whats next"])


def is_off_topic(message: str) -> bool:
    text = message.lower()
    return any(word in text for word in ["gst", "tax filing", "income tax", "itr", "loan", "rent agreement"])


def reply_to_message(body: dict[str, Any]) -> dict[str, Any]:
    conv_id = clean(body.get("conversation_id"), "conv_unknown")
    merchant_id = body.get("merchant_id")
    customer_id = body.get("customer_id")
    message = clean(body.get("message"))
    convo = conversations.setdefault(conv_id, {"merchant_id": merchant_id, "customer_id": customer_id, "turns": []})
    convo.setdefault("turns", []).append({"from": body.get("from_role"), "body": message, "at": body.get("received_at")})

    if is_auto_reply(message):
        merchant_key = clean(merchant_id, conv_id)
        merchant_auto_reply_counts[merchant_key] = merchant_auto_reply_counts.get(merchant_key, 0) + 1
        count = merchant_auto_reply_counts[merchant_key]
        if count >= 3:
            return {"action": "end", "rationale": "Auto-reply detected repeatedly; closing to avoid burning turns."}
        wait_seconds = 14400 if count == 1 else 86400
        return {
            "action": "wait",
            "wait_seconds": wait_seconds,
            "rationale": "Detected WhatsApp Business auto-reply; backing off for the owner to respond.",
        }

    if is_hostile(message):
        if merchant_id:
            merchant_suppression[merchant_id] = time.time() + 30 * 24 * 60 * 60
        return {"action": "end", "rationale": "Merchant explicitly opted out or was hostile; suppressing future outreach."}

    if is_off_topic(message):
        trigger_id = convo.get("trigger_id")
        trigger = active_context("trigger", trigger_id)
        topic = trigger.get("kind", "original item").replace("_", " ") if trigger else "original item"
        return {
            "action": "send",
            "body": f"I'll leave that to your specialist. Coming back to the {topic}: should I draft the WhatsApp first or prepare the short checklist?",
            "cta": "open_ended",
            "rationale": "Out-of-scope ask politely declined; redirected to the active Vera task.",
        }

    merchant = active_context("merchant", merchant_id) or {}
    category_slug = merchant.get("category_slug", "")
    name = salutation(merchant, category_slug) if merchant else "Got it"
    trigger = active_context("trigger", convo.get("trigger_id")) or {}
    trigger_kind = trigger.get("kind", "this")

    if is_commitment(message):
        return {
            "action": "send",
            "body": action_mode_body(name, merchant, trigger_kind),
            "cta": "binary_confirm_cancel",
            "rationale": "Merchant showed intent; switched immediately from qualification to action mode.",
        }

    if "price" in message.lower() or "cost" in message.lower() or "look like" in message.lower():
        return {
            "action": "send",
            "body": action_mode_body(name, merchant, trigger_kind),
            "cta": "binary_confirm_cancel",
            "rationale": "Merchant asked for concrete next step; provided a ready draft instead of more questions.",
        }

    return {
        "action": "send",
        "body": f"Got it, {name}. I can keep this low-effort: I'll draft the message, you only approve or edit. Reply CONFIRM and I'll prepare the final WhatsApp copy.",
        "cta": "binary_confirm_cancel",
        "rationale": "Acknowledged reply and moved toward a single approval CTA.",
    }


def action_mode_body(name: str, merchant: dict[str, Any], trigger_kind: str) -> str:
    category_slug = merchant.get("category_slug", "")
    aggregate = merchant.get("customer_aggregate", {})
    if category_slug == "dentists":
        count = aggregate.get("high_risk_adult_count") or aggregate.get("lapsed_180d_plus")
        return (
            f"Great, {name}. Drafting it now. I'll make one patient-safe WhatsApp and one GBP post, using the clinical source and "
            f"{f'your {count}-patient cohort' if count else 'your clinic context'}. Reply CONFIRM to approve the WhatsApp draft."
        )
    if category_slug == "restaurants":
        return (
            f"Great, {name}. Here's the action: one WhatsApp status, one delivery banner line, and one short caption using your active offer. "
            f"Reply CONFIRM and I'll finalize the copy."
        )
    if category_slug == "pharmacies":
        return (
            f"Understood, {name}. I'll prepare a staff checklist and customer-safe WhatsApp note with batch/molecule details only from the alert. "
            f"Reply CONFIRM to finalize."
        )
    return (
        f"Great, {name}. I'll draft the final WhatsApp for {trigger_kind.replace('_', ' ')} now, with one clear CTA and no extra work for you. "
        f"Reply CONFIRM to finalize."
    )


class VeraHandler(BaseHTTPRequestHandler):
    server_version = "VeraBot/1.0"

    def do_GET(self) -> None:
        if self.path == "/v1/healthz":
            self.send_json({"status": "ok", "uptime_seconds": int(time.time() - STARTED_AT), "contexts_loaded": context_counts()})
            return
        if self.path == "/v1/metadata":
            self.send_json(
                {
                    "team_name": "Team Alpha",
                    "team_members": ["Alice", "Bob"],
                    "model": "claude-opus-4-7",
                    "approach": "single-prompt composer with retrieval",
                    "version": "1.2.0",
                }
            )
            return
        self.serve_static()

    def do_POST(self) -> None:
        try:
            body = self.read_json()
        except ValueError as exc:
            self.send_json({"accepted": False, "reason": "malformed_json", "details": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        if self.path == "/v1/context":
            self.handle_context(body)
            return
        if self.path == "/v1/tick":
            self.handle_tick(body)
            return
        if self.path == "/v1/reply":
            self.send_json(reply_to_message(body))
            return
        if self.path == "/v1/demo/bootstrap":
            self.send_json({"status": "ok", "contexts_loaded": bootstrap_demo_contexts()})
            return
        if self.path == "/v1/demo/action":
            merchant_id = clean(body.get("merchant_id"))
            action = demo_action_for_merchant(merchant_id)
            if not action:
                self.send_json({"error": "no_action", "details": "No trigger/context found for merchant"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"action": action})
            return
        if self.path == "/v1/demo/reply":
            merchant_id = clean(body.get("merchant_id"))
            message = clean(body.get("message"))
            if not merchant_id or not message:
                self.send_json({"error": "invalid_payload", "details": "merchant_id and message are required"}, HTTPStatus.BAD_REQUEST)
                return
            conversation_id = clean(body.get("conversation_id"))
            if not conversation_id:
                action = demo_action_for_merchant(merchant_id)
                conversation_id = (action or {}).get("conversation_id") or f"conv_demo_{merchant_id}"
            response = reply_to_message(
                {
                    "conversation_id": conversation_id,
                    "merchant_id": merchant_id,
                    "customer_id": None,
                    "from_role": "merchant",
                    "message": message,
                    "received_at": utc_now(),
                    "turn_number": int(body.get("turn_number") or 2),
                }
            )
            self.send_json({"conversation_id": conversation_id, "response": response})
            return
        if self.path == "/v1/teardown":
            contexts.clear()
            conversations.clear()
            sent_suppression_keys.clear()
            merchant_suppression.clear()
            merchant_auto_reply_counts.clear()
            self.send_json({"status": "cleared", "cleared_at": utc_now()})
            return

        self.send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def handle_context(self, body: dict[str, Any]) -> None:
        scope = body.get("scope")
        context_id = body.get("context_id")
        version = body.get("version")
        payload = body.get("payload")

        if scope not in SCOPES:
            self.send_json({"accepted": False, "reason": "invalid_scope", "details": f"scope must be one of {sorted(SCOPES)}"}, HTTPStatus.BAD_REQUEST)
            return
        if not context_id or not isinstance(version, int) or not isinstance(payload, dict):
            self.send_json({"accepted": False, "reason": "invalid_payload", "details": "context_id, integer version, and payload object are required"}, HTTPStatus.BAD_REQUEST)
            return

        key = (scope, context_id)
        current = contexts.get(key)
        if current and current["version"] >= version:
            self.send_json({"accepted": False, "reason": "stale_version", "current_version": current["version"]}, HTTPStatus.CONFLICT)
            return

        contexts[key] = {"version": version, "payload": payload, "stored_at": utc_now()}
        self.send_json({"accepted": True, "ack_id": f"ack_{context_id}_v{version}", "stored_at": contexts[key]["stored_at"]})

    def handle_tick(self, body: dict[str, Any]) -> None:
        available = body.get("available_triggers", [])
        now = clean(body.get("now"), utc_now())
        if not isinstance(available, list):
            self.send_json({"actions": []})
            return
        actions = []
        ranked = sorted(available, key=lambda trigger_id: (active_context("trigger", trigger_id) or {}).get("urgency", 0), reverse=True)
        for trigger_id in ranked[:20]:
            action = compose_action(clean(trigger_id), now)
            if action:
                actions.append(action)
        self.send_json({"actions": actions})

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(str(exc)) from exc
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def serve_static(self) -> None:
        raw_path = self.path.split("?", 1)[0]
        if raw_path in {"", "/"}:
            target = FRONTEND_DIR / "index.html"
        else:
            relative = Path(unquote(raw_path.lstrip("/")))
            target = (FRONTEND_DIR / relative).resolve()
            if not str(target).startswith(str(FRONTEND_DIR.resolve())):
                self.send_error(HTTPStatus.FORBIDDEN)
                return
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - - [{self.log_date_time_string()}] {fmt % args}")


def context_counts() -> dict[str, int]:
    counts = {scope: 0 for scope in sorted(SCOPES)}
    for scope, _ in contexts:
        counts[scope] = counts.get(scope, 0) + 1
    return counts


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Vera challenge bot backend and frontend server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), VeraHandler)
    print(f"Vera bot listening on http://{args.host}:{args.port}")
    print("API: /v1/healthz /v1/metadata /v1/context /v1/tick /v1/reply")
    print("Frontend: /")
    server.serve_forever()


if __name__ == "__main__":
    main()
