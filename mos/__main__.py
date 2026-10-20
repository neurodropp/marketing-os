"""Run from the repository root with python3 -m mos."""
import argparse
import json
import sys

from . import core as c
from . import onboarding, workspace, processes


def main(argv=None):
    p = argparse.ArgumentParser(description="Local Marketing OS workspace, memory and handoff utilities")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Validate the repository graph, skills and workflows")
    q = sub.add_parser("process-list", help="List operational process contracts")
    q.add_argument("--domain")
    q = sub.add_parser("process-show", help="Show one SOP contract and input template")
    q.add_argument("process_id")
    q = sub.add_parser("process-start", help="Create a pinned process work order; does not invoke an LLM")
    q.add_argument("project")
    q.add_argument("--process", required=True)
    q.add_argument("--id", required=True)
    q.add_argument("--objective", required=True)
    q.add_argument("--inputs-file", required=True)
    q = sub.add_parser("process-finish", help="Record artifacts and quality evidence for a process")
    q.add_argument("project")
    q.add_argument("--run", required=True)
    q.add_argument("--file", required=True)
    q = sub.add_parser("process-status", help="Read process state and verify pinned evidence")
    q.add_argument("project")
    q.add_argument("--run", required=True)
    q = sub.add_parser("workspace-init", help="Create a standalone brand folder with guided onboarding")
    q.add_argument("path")
    q.add_argument("--id", required=True)
    q.add_argument("--brand", required=True)
    q = sub.add_parser("onboarding-status", help="Resume intake and return the next question block")
    q.add_argument("project")
    q = sub.add_parser("onboarding-answer", help="Persist sourced intake answers with revision checking")
    q.add_argument("project")
    q.add_argument("--file", required=True)
    q = sub.add_parser("onboarding-confirm", help="Record explicit confirmation of the exact intake summary")
    q.add_argument("project")
    q.add_argument("--digest", required=True)
    q.add_argument("--by", required=True)
    q.add_argument("--authorization", required=True)
    q = sub.add_parser("init", help="Create an isolated project workspace")
    q.add_argument("path")
    q.add_argument("--id", required=True)
    q.add_argument("--brand", required=True)
    q = sub.add_parser("memory-add", help="Append a memory proposal from a JSON payload")
    q.add_argument("project")
    q.add_argument("--file", required=True)
    q = sub.add_parser("memory-accept", help="Record an authorized acceptance; not an authentication mechanism")
    q.add_argument("project")
    q.add_argument("id")
    q.add_argument("--by", required=True)
    q.add_argument("--authorization", required=True)
    q.add_argument("--supersede", action="append", default=[])
    q = sub.add_parser("memory-reject", help="Reject a proposal while preserving its history")
    q.add_argument("project")
    q.add_argument("id")
    q.add_argument("--by", required=True)
    q.add_argument("--reason", required=True)
    q = sub.add_parser("memory-search", help="Find active records by case-insensitive keyword AND matching")
    q.add_argument("project")
    q.add_argument("query", nargs="?", default="")
    q = sub.add_parser("plan", help="Create a version-pinned run; does not invoke agents or tools")
    q.add_argument("project")
    q.add_argument("--workflow", required=True)
    q.add_argument("--id", required=True)
    q.add_argument("--objective", required=True)
    q = sub.add_parser("complete-step", help="Record an actual handoff after checking dependencies")
    q.add_argument("project")
    q.add_argument("--run", required=True)
    q.add_argument("--step", required=True)
    q.add_argument("--file", required=True)
    q = sub.add_parser("export", help="Write a local portable Markdown bundle; no upload")
    q.add_argument("--workflow", required=True, help="Registered workflow ID, or 'full' for the complete reference library")
    q.add_argument("--out", required=True)
    q.add_argument("--project")
    q.add_argument("--memory-id", action="append", default=[])
    q.add_argument("--include-confidential", action="store_true")
    q = sub.add_parser("route", help="Return lexical candidates; the orchestrator makes the final routing decision")
    q.add_argument("request")
    a = p.parse_args(argv)
    try:
        if a.command == "validate":
            result = c.validate_repo()
        elif a.command == "process-list":
            result = [{"id": x["id"], "name": x["name"], "agent": x["agent"], "path": x["path"]}
                      for x in processes.catalog()["processes"] if not a.domain or x["domain"] == a.domain]
        elif a.command == "process-show":
            result = processes.show(a.process_id)
        elif a.command == "process-start":
            result = processes.start(a.project, a.process, a.id, a.objective, c.read(a.inputs_file))
        elif a.command == "process-finish":
            result = processes.finish(a.project, a.run, c.read(a.file))
        elif a.command == "process-status":
            result = processes.status(a.project, a.run)
        elif a.command == "workspace-init":
            result = workspace.initialize(a.path, a.id, a.brand)
        elif a.command == "onboarding-status":
            result = onboarding.status(a.project)
        elif a.command == "onboarding-answer":
            result = onboarding.answer(a.project, c.read(a.file))
        elif a.command == "onboarding-confirm":
            result = onboarding.confirm(a.project, a.digest, a.by, a.authorization)
        elif a.command == "init":
            result = c.initialize(a.path, a.id, a.brand)
        elif a.command == "memory-add":
            result = c.memory_add(a.project, c.read(a.file))
        elif a.command == "memory-accept":
            result = c.memory_accept(a.project, a.id, a.by, a.authorization, a.supersede)
        elif a.command == "memory-reject":
            result = c.memory_reject(a.project, a.id, a.by, a.reason)
        elif a.command == "memory-search":
            result = c.search_memory(a.project, a.query)
        elif a.command == "plan":
            result = c.create_run(a.project, a.workflow, a.id, a.objective)
        elif a.command == "complete-step":
            result = c.complete_step(a.project, a.run, a.step, c.read(a.file))
        elif a.command == "export":
            result = c.export_bundle(a.workflow, a.out, a.project, a.memory_id, a.include_confidential)
        elif a.command == "route":
            reg = c.read(c.ROOT / "registry.json")
            candidates = []
            for s in reg["skills"]:
                matches = [k for k in s["keywords"] if k.casefold() in a.request.casefold()]
                if matches:
                    candidates.append({"skill": s["id"], "agent": s["agent"], "matched_terms": matches})
            result = {"candidates": candidates, "note": "Lexical hints only; inspect intent, scope and memory before selecting"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (c.Invalid, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
