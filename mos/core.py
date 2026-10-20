"""Deterministic local operations; the host LLM performs reasoning and tool use."""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KINDS = {"fact", "research", "insight", "strategy", "decision", "asset", "metric", "learning", "session"}
SENSITIVITIES = {"public", "internal", "confidential"}


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def identifier(value):
    require(isinstance(value, str) and len(value) <= 64 and bool(ID.fullmatch(value)), f"Invalid identifier: {value!r}")
    return value


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def subject_key(record):
    return record["kind"], " ".join(record["subject"].casefold().split())


def read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Invalid(f"Cannot read JSON at {path}: {exc}") from exc


def safe(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts, "Path must stay inside its root")
    p = root
    for part in rel.parts:
        p = p / part
        require(not p.is_symlink(), f"Symlink is not allowed: {p}")
    require(p.resolve().is_relative_to(root), "Path escapes root")
    return p


def save(path, obj, *, create=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if create:
        with path.open("x", encoding="utf-8") as f:
            f.write(data)
    else:
        tmp = path.with_name(path.name + ".tmp")
        require(not tmp.exists() and not tmp.is_symlink(), f"Unexpected temporary file: {tmp}")
        with tmp.open("x", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)


@contextlib.contextmanager
def locked(project):
    lock = safe(project, ".mos-lock")
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise Invalid("Project is locked by another operation; inspect before removing a stale lock") from exc
    try:
        yield
    finally:
        lock.rmdir()


def project_config(project):
    p = Path(project).resolve()
    cfg = read(safe(p, "project.json"))
    require(cfg.get("schema_version") == "1.0", "Unsupported project schema; migrate explicitly")
    identifier(cfg.get("project_id"))
    require(isinstance(cfg.get("brand"), str) and bool(cfg["brand"].strip()), "Brand is required")
    return cfg


def initialize(path, project_id, brand):
    identifier(project_id)
    require(bool(brand.strip()), "Brand is required")
    p = Path(path)
    require(not p.exists() and not p.is_symlink(), "Project destination already exists; refusing overwrite")
    p.mkdir(parents=True)
    cfg = {
        "schema_version": "1.0", "project_id": project_id, "brand": brand,
        "created_at": now(), "language": "en", "markets": [], "objectives": [],
        "capabilities": {"file_access": True, "web_research": False, "subagents": False, "external_tools": []},
        "permissions": {"external_actions": [], "spend_limit": None},
        "runtime": {"mode": "single-agent", "max_revision_cycles": 2},
    }
    save(p / "project.json", cfg, create=True)
    for folder in ("memory/records", "artifacts", "runs"):
        (p / folder).mkdir(parents=True)
    (p / "README.md").write_text(
        "# Private project workspace\n\nFill project.json from verified project facts. "
        "Add memory proposals with `python3 -m mos memory-add`; accept only with recorded authority. "
        "This workspace is ignored by the framework repository. Back it up in a private location. "
        "Do not store passwords, tokens or raw customer exports here.\n", encoding="utf-8")
    return cfg


def records(project):
    cfg = project_config(project)
    result = {}
    folder = safe(project, "memory/records")
    for f in sorted(folder.glob("*.json")):
        require(not f.is_symlink(), "Memory symlink refused")
        r = read(f)
        require(r.get("project_id") == cfg["project_id"], "Cross-project memory record refused")
        identifier(r.get("id"))
        require(r.get("schema_version") == "1.0", "Unsupported memory schema")
        require(type(r.get("version")) is int and r["version"] > 0, "Invalid memory version")
        require(r.get("kind") in KINDS and r.get("status") in {"proposed", "approved", "rejected"}, "Invalid memory type/status")
        require(r.get("sensitivity") in SENSITIVITIES, "Invalid sensitivity")
        require(isinstance(r.get("subject"), str) and r["subject"].strip(), "Missing subject")
        require(isinstance(r.get("content"), str) and r["content"].strip(), "Missing content")
        require(isinstance(r.get("evidence"), list) and all(isinstance(x, str) and x.strip() for x in r["evidence"]), "Invalid evidence")
        require(isinstance(r.get("supersedes"), list), "Invalid supersedes")
        for target in r["supersedes"]:
            identifier(target)
        require(f.name == f"{r['id']}.v{r['version']:04}.json", "Memory filename/version mismatch")
        old = result.get(r["id"])
        if not old or old["version"] < r["version"]:
            result[r["id"]] = r
    return result


def active_records(project):
    rs = records(project)
    replaced = {i for r in rs.values() if r["status"] == "approved" for i in r["supersedes"]}
    return {i: r for i, r in rs.items() if i not in replaced and r["status"] != "rejected"}


def memory_add(project, payload):
    cfg = project_config(project)
    require(isinstance(payload, dict), "Memory payload must be an object")
    allowed = {"id", "kind", "subject", "content", "evidence", "sensitivity", "review_after"}
    require(set(payload) <= allowed, "Unexpected payload fields; approvals/version/project scope are controlled separately")
    identifier(payload.get("id"))
    require(payload.get("kind") in KINDS, "Unknown memory kind")
    for key in ("subject", "content"):
        require(isinstance(payload.get(key), str) and payload[key].strip(), f"{key} is required")
    evidence = payload.get("evidence", [])
    require(isinstance(evidence, list) and all(isinstance(v, str) and v.strip() for v in evidence), "Evidence must be a list of source references")
    require(payload.get("sensitivity", "internal") in SENSITIVITIES, "Unknown sensitivity")
    if payload.get("review_after"):
        try:
            dt.date.fromisoformat(payload["review_after"])
        except (ValueError, TypeError) as exc:
            raise Invalid("review_after must be YYYY-MM-DD") from exc
    with locked(project):
        require(payload["id"] not in records(project), "Memory ID already exists; create a new proposal and supersede explicitly")
        r = {**payload, "schema_version": "1.0", "project_id": cfg["project_id"],
             "version": 1, "status": "proposed", "evidence": evidence,
             "sensitivity": payload.get("sensitivity", "internal"), "supersedes": [],
             "created_at": now(), "updated_at": now(), "approval": None}
        save(safe(project, f"memory/records/{r['id']}.v0001.json"), r, create=True)
    return r


def memory_accept(project, record_id, by, authorization, supersedes=()):
    identifier(record_id)
    require(bool(by.strip()) and bool(authorization.strip()), "Approver and authorization evidence are required")
    with locked(project):
        rs = active_records(project)
        require(record_id in rs, "Unknown or inactive memory ID")
        r = rs[record_id]
        require(r["status"] == "proposed", "Only proposals may be accepted")
        require(bool(r["evidence"]), "Approved memory requires a source; use a user decision reference for strategy")
        targets = set(supersedes)
        require(record_id not in targets, "A record cannot supersede itself")
        peers = {i for i, v in rs.items() if i != record_id and v["status"] == "approved"
                 and subject_key(v) == subject_key(r)}
        require(targets == peers, "Explicitly supersede all approved records with the same kind and subject; unrelated supersession is refused")
        revised = {**r, "version": r["version"] + 1, "status": "approved", "updated_at": now(),
                   "supersedes": sorted(targets), "approval": {"by": by, "authorization": authorization}}
        save(safe(project, f"memory/records/{record_id}.v{revised['version']:04}.json"), revised, create=True)
    return revised


def memory_reject(project, record_id, by, reason):
    identifier(record_id)
    require(bool(by.strip()) and bool(reason.strip()), "Reviewer and rejection reason are required")
    with locked(project):
        rs = active_records(project)
        require(record_id in rs and rs[record_id]["status"] == "proposed", "Only an active proposal may be rejected")
        r = rs[record_id]
        revised = {**r, "version": r["version"] + 1, "status": "rejected", "updated_at": now(),
                   "rejection": {"by": by, "reason": reason}}
        save(safe(project, f"memory/records/{record_id}.v{revised['version']:04}.json"), revised, create=True)
    return revised


def search_memory(project, query=""):
    terms = query.casefold().split()
    rs = active_records(project)
    selected = [r for r in rs.values() if all(t in (r["subject"] + " " + r["content"]).casefold() for t in terms)]
    groups = {}
    for r in rs.values():
        groups.setdefault(subject_key(r), []).append(r["id"])
    conflicts = [ids for ids in groups.values() if len(ids) > 1]
    today = dt.date.today().isoformat()
    return {"records": selected, "conflicts": conflicts,
            "review_due": [r["id"] for r in selected if r.get("review_after") and r["review_after"] <= today]}


def validate_repo(root=ROOT):
    root = Path(root)
    reg = read(safe(root, "registry.json"))
    require(reg.get("schema_version") == "1.0", "Unsupported registry schema")
    agents, skills = {}, {}
    for key, dest in (("agents", agents), ("skills", skills)):
        for item in reg[key]:
            identifier(item["id"])
            require(item["id"] not in dest, f"Duplicate {key} ID")
            dest[item["id"]] = item
            require(safe(root, item["path"]).is_file(), f"Missing {item['path']}")
    taxonomy = read(safe(root, "catalog/taxonomy.json"))
    seen = set()
    domains = {d["id"] for d in taxonomy["domains"]}
    for d in taxonomy["domains"]:
        for obj in [d] + d["processes"] + [c for p in d["processes"] for c in p["capabilities"]]:
            require(obj["id"] not in seen, "Duplicate taxonomy ID")
            seen.add(obj["id"])
        require(d["skill"] in skills, "Domain skill is missing")
    for sid, s in skills.items():
        require(s["agent"] in agents and sid in agents[s["agent"]]["skills"], "Agent/skill ownership mismatch")
        require(s["domain"] is None or s["domain"] in domains, "Unknown domain")
        require(bool(re.fullmatch(r"\d+\.\d+\.\d+", s["version"])), "Skill version must use semantic versioning")
        text = safe(root, s["path"]).read_text(encoding="utf-8")
        require(text.startswith("---\n") and "\n---\n" in text[4:], "Skill frontmatter required")
        front = text.split("---", 2)[1]
        require(f"name: {sid}\n" in front, "Skill name/folder mismatch")
        require(bool(re.search(r"^description: .+", front, re.M)), "Skill description required")
        require(safe(root, s["path"]).parent.name == sid, "Skill folder mismatch")
        require(f'version: "{s["version"]}"' in front, "Registry and skill version disagree")
        for ref in s.get("references", []):
            require(safe(root, ref).is_file(), f"Missing skill reference {ref}")
    for a in agents.values():
        require(all(s in skills for s in a["skills"]), "Unknown skill in agent")
    from .processes import validate_catalog
    process_specs = validate_catalog(root, reg, taxonomy)
    workflow_ids = set()
    for entry in reg["workflows"]:
        identifier(entry["id"])
        require(entry["id"] not in workflow_ids, "Duplicate workflow ID")
        workflow_ids.add(entry["id"])
        w = read(safe(root, entry["path"]))
        require(w["id"] == entry["id"], "Workflow ID mismatch")
        steps = {s["id"]: s for s in w["steps"]}
        require(len(steps) == len(w["steps"]) and bool(steps), "Duplicate or empty workflow steps")
        pending, done = set(steps), set()
        for s in steps.values():
            identifier(s["id"])
            require(s["agent"] in agents, "Unknown workflow agent")
            require(set(s["depends_on"]) <= set(steps), "Unknown dependency")
            process_ids = s.get("process_ids", [])
            require(isinstance(process_ids, list) and len(process_ids) == len(set(process_ids)),
                    "Workflow process IDs must be a unique array")
            if agents[s["agent"]].get("domain") is not None:
                require(bool(process_ids), "Domain workflow step must map to operational processes")
            for pid in process_ids:
                require(pid in process_specs and process_specs[pid]["agent"] == s["agent"],
                        "Workflow process ownership mismatch")
        while pending:
            ready = {i for i in pending if set(steps[i]["depends_on"]) <= done}
            require(bool(ready), "Workflow contains a dependency cycle")
            done |= ready
            pending -= ready
    return {"agents": len(agents), "skills": len(skills), "domains": len(domains),
            "processes": sum(len(d["processes"]) for d in taxonomy["domains"]),
            "capabilities": sum(len(p["capabilities"]) for d in taxonomy["domains"] for p in d["processes"]),
            "workflows": len(workflow_ids), "operational_sops": len(process_specs)}


def workflow_context(workflow_id, root=ROOT):
    validate_repo(root)
    reg = read(Path(root) / "registry.json")
    matches = [w for w in reg["workflows"] if w["id"] == workflow_id]
    require(len(matches) == 1, "Unknown workflow")
    w = read(safe(root, matches[0]["path"]))
    agent_ids = {s["agent"] for s in w["steps"]} | {"orchestrator"}
    agents = [a for a in reg["agents"] if a["id"] in agent_ids]
    skill_ids = {sid for a in agents for sid in a["skills"]}
    skills = [s for s in reg["skills"] if s["id"] in skill_ids]
    return reg, w, agents, skills


def create_run(project, workflow_id, run_id, objective, root=ROOT):
    identifier(run_id)
    require(bool(objective.strip()), "Run objective is required")
    cfg = project_config(project)
    reg, w, agents, skills = workflow_context(workflow_id, root)
    paths = [a["path"] for a in agents] + [s["path"] for s in skills] + [p for s in skills for p in s["references"]]
    paths += [next(e["path"] for e in reg["workflows"] if e["id"] == workflow_id)]
    paths += ["protocols/orchestration.md", "protocols/second-brain.md", "protocols/contracts.md",
              "protocols/process-execution.md"]
    run = {"schema_version": "1.0", "project_id": cfg["project_id"], "id": run_id,
           "objective": objective, "workflow_id": workflow_id, "release": reg["release"],
           "created_at": now(), "status": "in-progress", "events": [],
           "approved_memory_snapshot": {i: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
                                        for i, r in active_records(project).items() if r["status"] == "approved"},
           "pinned_files": {p: hashlib.sha256(safe(root, p).read_bytes()).hexdigest() for p in paths},
           "steps": [{**s, "status": "pending", "handoff": None} for s in w["steps"]]}
    with locked(project):
        save(safe(project, f"runs/{run_id}.json"), run, create=True)
    return run


def complete_step(project, run_id, step_id, handoff, root=ROOT):
    identifier(run_id)
    cfg = project_config(project)
    with locked(project):
        path = safe(project, f"runs/{run_id}.json")
        run = read(path)
        require(run["project_id"] == cfg["project_id"], "Cross-project run refused")
        memory_snapshot = {i: hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
                           for i, r in active_records(project).items() if r["status"] == "approved"}
        require(run["approved_memory_snapshot"] == memory_snapshot,
                "Approved project memory changed; reconcile context and create a replacement run")
        for p, digest in run["pinned_files"].items():
            require(hashlib.sha256(safe(root, p).read_bytes()).hexdigest() == digest,
                    "Run definitions changed; create a new run or perform an explicit migration")
        matches = [s for s in run["steps"] if s["id"] == step_id]
        require(len(matches) == 1, "Unknown step")
        step = matches[0]
        require(step["status"] == "pending", "Step is already resolved; use a new run for revision")
        done = {s["id"] for s in run["steps"] if s["status"] == "done"}
        require(set(step["depends_on"]) <= done, "Dependencies have not completed")
        from . import processes
        for prior in run["steps"]:
            if prior["status"] == "done":
                for linked_id in prior["handoff"].get("process_runs", []):
                    processes.status(project, linked_id, root)
        require(handoff.get("project_id") == cfg["project_id"] and handoff.get("step_id") == step_id, "Handoff scope mismatch")
        for key in ("deliverable", "execution_mode", "acceptance"):
            require(isinstance(handoff.get(key), str) and handoff[key].strip(), f"Handoff {key} is required")
        require(handoff["execution_mode"] in {"role-pass", "delegated"}, "Invalid execution mode")
        if handoff["execution_mode"] == "delegated":
            require(cfg["capabilities"]["subagents"], "Project does not declare subagent capability")
        for key in ("sources", "assumptions", "memory_proposals"):
            require(isinstance(handoff.get(key), list), f"Handoff {key} must be an array")
        required_processes = step.get("process_ids", [])
        if required_processes:
            linked = handoff.get("process_runs")
            require(isinstance(linked, list) and all(isinstance(x, str) for x in linked)
                    and len(linked) == len(set(linked)), "Unique completed process run IDs required")
            completed = [processes.status(project, pid, root) for pid in linked]
            require(len(completed) == len(required_processes)
                    and {p["process_id"] for p in completed} == set(required_processes),
                    "Handoff must cover every process mapped to the step exactly once")
            require(all(p["status"] in {"ready", "executed"} for p in completed),
                    "Workflow step requires ready/executed process artifacts")
        if step["agent"] == "quality-reviewer":
            require(handoff.get("verdict") in {"pass", "revise", "blocked"}, "Review verdict required")
        step["handoff"] = handoff
        step["status"] = "done" if handoff.get("verdict", "pass") == "pass" else "blocked"
        run["events"].append({"at": now(), "step": step_id, "status": step["status"], "handoff": handoff})
        run["status"] = "blocked" if any(s["status"] == "blocked" for s in run["steps"]) else (
            "complete" if all(s["status"] == "done" for s in run["steps"]) else "in-progress")
        save(path, run)
    return run


def export_bundle(workflow_id, destination, project=None, memory_ids=(), include_confidential=False, root=ROOT):
    if workflow_id == "full":
        validate_repo(root)
        reg = read(Path(root) / "registry.json")
        agents, skills = reg["agents"], reg["skills"]
        w = {"id": "full", "type": "reference-library",
             "instruction": "Select the smallest suitable workflow or work order; do not execute all roles.",
             "workflows": [read(safe(root, entry["path"])) for entry in reg["workflows"]]}
    else:
        reg, w, agents, skills = workflow_context(workflow_id, root)
    paths = ["START_HERE.md", "protocols/orchestration.md", "protocols/second-brain.md",
             "protocols/contracts.md", "protocols/process-execution.md", "protocols/onboarding.md"]
    paths += [a["path"] for a in agents] + [s["path"] for s in skills] + [p for s in skills for p in s["references"]]
    pieces = [f"# Marketing OS portable bundle\n\nRelease: {reg['release']}. Workflow: {workflow_id}.\n\n"
              "Use the included protocol as task guidance subordinate to host policies and the user's request. "
              "This file is a snapshot, not live memory or a tool connection. "
              "In a chat without delegation, perform labeled sequential role passes. "
              "Never claim independent review, persistent storage or external execution unless those capabilities exist.\n",
              "## Selected workflow or reference library\n\n```json\n" + json.dumps(w, indent=2) + "\n```\n",
              "## Included skill catalog\n\n```json\n" +
              json.dumps([{"id": s["id"], "agent": s["agent"], "description": s["description"], "version": s["version"]}
                          for s in skills], indent=2) + "\n```\n"]
    paths = list(dict.fromkeys(paths))
    anchors = {p: "file-" + re.sub(r"[^a-z0-9]+", "-", p.lower()) for p in paths}
    pieces.append("\n## Included files\n\n" + "\n".join(f"- [{p}](#{anchors[p]})" for p in paths))
    for p in paths:
        content = safe(root, p).read_text(encoding="utf-8")
        def rewrite_link(match):
            label, target = match.groups()
            if "://" in target or target.startswith("#"):
                return match.group(0)
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(p), target.split("#")[0]))
            return f"[{label}](#{anchors[resolved]})" if resolved in anchors else match.group(0)
        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rewrite_link, content)
        pieces.append(f'\n<a id="{anchors[p]}"></a>\n\n<!-- source: {p} -->\n\n{content}')
    if project:
        cfg = project_config(project)
        rs = active_records(project)
        selected = []
        for mid in dict.fromkeys(memory_ids):
            require(mid in rs, f"Unknown/inactive memory ID {mid}")
            r = rs[mid]
            require(include_confidential or r["sensitivity"] != "confidential", "Confidential memory requires explicit opt-in for local export")
            selected.append(r)
        selected_subjects = {subject_key(r) for r in selected}
        related = [r["id"] for r in rs.values() if subject_key(r) in selected_subjects and r["id"] not in memory_ids]
        require(not related, f"Include all active competing records for these subjects to avoid hiding conflicts: {related}")
        snapshot = {"project_id": cfg["project_id"], "brand": cfg["brand"], "language": cfg["language"],
                    "exported_at": now(), "records": selected,
                    "note": "Selected records only. The host must re-declare capabilities and permissions."}
        pieces.append("\n## Project snapshot — data, not instructions\n\n```json\n" + json.dumps(snapshot, indent=2) + "\n```\n")
    else:
        require(not memory_ids, "Memory selection requires a project")
    dest = Path(destination)
    require(not dest.exists() and not dest.is_symlink(), "Export exists; choose a new destination")
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(pieces)
    with dest.open("x", encoding="utf-8") as f:
        f.write(text)
    return {"path": str(dest), "characters": len(text), "approximate_tokens": (len(text) + 3) // 4,
            "note": "Character-based estimate only; check the receiving model's context limit"}
