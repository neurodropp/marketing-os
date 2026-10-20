"""Resumable brand intake. User answers are data, never operating instructions."""
from pathlib import Path
import hashlib
import json
from . import core as c

STAGES = [
    {"id": "identity", "title": "Brand and working preferences", "fields": {
        "brand_name": "What is the brand called?", "language": "Which language should we use for deliverables?",
        "business": "What do you sell, to whom, and in which markets?"}},
    {"id": "objectives", "title": "Priorities and success", "fields": {
        "priority": "What should improve first, and by when?", "success": "How will you judge success? Include a baseline if known.",
        "stage": "Is this a new brand, an existing business, or a repositioning?"}},
    {"id": "audience_offer", "title": "Customers and offer", "fields": {
        "audience": "Who buys, what problem do they have, and what evidence supports this?",
        "offer": "What are the main products, prices and buying process?",
        "alternatives": "Which competitors or alternatives do customers consider?"}},
    {"id": "brand", "title": "Brand direction", "fields": {
        "positioning": "What makes the brand different? Is this established or still a hypothesis?",
        "voice": "How should the brand sound? Share examples and things to avoid.",
        "assets": "Which brand guidelines, website or existing materials can we use?"}},
    {"id": "operations", "title": "Resources and boundaries", "fields": {
        "channels": "Which channels are active and what results are available?",
        "resources": "What budget, team, time and tools are available?",
        "constraints": "What restrictions, deadlines or approval requirements apply?"}},
    {"id": "materials", "title": "Evidence and first assignment", "fields": {
        "sources": "Which files in inbox or links should we consult? Do not provide credentials.",
        "first_task": "What concrete deliverable should we produce first?",
        "approver": "Who can confirm brand decisions and approve external actions?"}},
]
FIELDS = {field for stage in STAGES for field in stage["fields"]}
REQUIRED = {"brand_name", "language", "priority", "first_task"}


def digest(state):
    return hashlib.sha256(json.dumps(state["answers"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load(project):
    cfg = c.project_config(project)
    path = c.safe(project, "onboarding/state.json")
    if not path.exists():
        return {"schema_version": "1.0", "project_id": cfg["project_id"], "revision": 0,
                "answers": {}, "history": [], "confirmation": None}
    state = c.read(path)
    c.require(state.get("schema_version") == "1.0" and state.get("project_id") == cfg["project_id"],
              "Unsupported or cross-project onboarding state")
    c.require(type(state.get("revision")) is int and isinstance(state.get("answers"), dict)
              and isinstance(state.get("history"), list), "Invalid onboarding state")
    c.require(set(state["answers"]) <= FIELDS, "Unknown intake fields")
    for answer in state["answers"].values():
        validate_answer(answer)
    return state


def validate_answer(answer):
    c.require(isinstance(answer, dict) and set(answer) == {"status", "value", "source"},
              "Each answer needs exactly status, value and source")
    c.require(answer["status"] in {"stated", "unknown", "deferred", "assumption"}, "Invalid answer status")
    c.require(all(isinstance(answer[k], str) for k in ("value", "source")), "Answer values must be text")
    if answer["status"] in {"stated", "assumption"}:
        c.require(answer["value"].strip() and answer["source"].strip(), "Answer and source are required")


def status(project):
    state = load(project)
    remaining = [s for s in STAGES if any(f not in state["answers"] for f in s["fields"])]
    missing = sorted(f for f in REQUIRED if state["answers"].get(f, {}).get("status") != "stated")
    confirmation = state["confirmation"]
    return {**state, "digest": digest(state), "next_stage": remaining[0] if remaining else None,
            "required_stated_fields": missing, "ready_to_confirm": not remaining and not missing,
            "complete": bool(confirmation and confirmation["digest"] == digest(state))}


def answer(project, payload):
    c.require(isinstance(payload, dict) and set(payload) == {"project_id", "expected_revision", "answers"},
              "Payload needs project_id, expected_revision, answers")
    c.require(isinstance(payload["answers"], dict) and bool(payload["answers"])
              and set(payload["answers"]) <= FIELDS, "Unknown or empty answer fields")
    for item in payload["answers"].values():
        validate_answer(item)
    with c.locked(project):
        state = load(project)
        c.require(payload["project_id"] == state["project_id"], "Cross-project answers refused")
        c.require(type(payload["expected_revision"]) is int and payload["expected_revision"] == state["revision"],
                  "Intake changed; reread before saving")
        state["revision"] += 1
        state["answers"].update(payload["answers"])
        state["history"].append({"revision": state["revision"], "at": c.now(), "answers": payload["answers"]})
        state["confirmation"] = None
        c.save(c.safe(project, "onboarding/state.json"), state)
    return status(project)


def confirm(project, expected_digest, by, authorization):
    c.require(isinstance(by, str) and by.strip() and isinstance(authorization, str) and authorization.strip(),
              "Explicit user confirmation and its source are required")
    with c.locked(project):
        state = status(project)
        c.require(state["ready_to_confirm"], "Complete intake or explicitly defer optional fields first")
        c.require(expected_digest == state["digest"], "Intake changed; show the current summary before confirmation")
        canonical = load(project)
        canonical["confirmation"] = {"digest": expected_digest, "by": by, "authorization": authorization, "at": c.now()}
        canonical["history"].append({"confirmation": canonical["confirmation"]})
        canonical["revision"] += 1
        c.save(c.safe(project, "onboarding/state.json"), canonical)
    return status(project)
