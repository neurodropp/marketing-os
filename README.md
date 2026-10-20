# Marketing OS

A portable agentic framework for marketing and brand projects, with a durable second brain for each project.

The framework combines **16 marketing domains, 108 processes and 540 capabilities** with **19 agent roles and 19 modular skills**: an orchestrator, 16 domain specialists, a memory steward and a quality reviewer. Domain coverage is a planning taxonomy; it is not 540 fully implemented automations.

The repository is in English. Project deliverables can use the project's configured language.

## What you can use today

- Run a marketing assignment through documented agent roles and focused skills.
- Start a private project workspace with versioned memory, sources, approvals and conflicts.
- Use ten dependency-aware workflows: brand foundation, campaigns, offers, content, reputation, tracking incidents, retention, lifecycle, performance and strategic reviews.
- Export a self-contained Markdown bundle for a chat that cannot read the repository.
- Validate registry references and workflow dependencies, pin a run to exact skill definitions, and record accepted handoffs.
- Add or update skills, agents and workflows without changing the core project memory.

The Python utilities perform local state management. They do **not** call an LLM, spawn agents, authenticate users, publish content, spend money or connect accounts. The host AI environment supplies those capabilities where available.

## Choose an entry point

| Environment | Start here | Actual behavior |
| --- | --- | --- |
| AI assistant with repository access | Ask it to read [START_HERE.md](START_HERE.md) | Loads selected roles, skills and project memory on demand. |
| Chat with file upload or pasted context | Upload a generated Markdown bundle | Performs sequential role passes; persistence requires saving and reattaching checkpoints. |
| Agent runtime with delegation | Use the same protocols and handoff contracts | Real subagents are possible only if supported and authorized by that host. |
| Developer integration | Use `mos/`, registry, workflows and schemas | Provides a local control plane to integrate with a model SDK or tool runner. |

No repository URL can guarantee automatic import, persistent memory or real multi-agent execution in every AI product. See [portability](docs/PORTABILITY.md) for the supported modes and limitations.

## Quick start

Python **3.10 or later** is required for local utilities. There are no third-party Python dependencies.

```bash
git clone https://github.com/neurodropp/marketing-os.git
cd marketing-os
python3 -m mos validate
python3 -m unittest discover -s tests -v

python3 -m mos init projects/demo-brand --id demo-brand --brand "Demo Brand"
python3 -m mos memory-add projects/demo-brand --file examples/memory-proposal.json
python3 -m mos memory-search projects/demo-brand audience
```

The example is synthetic. To accept it for a demonstration:

```bash
python3 -m mos memory-accept projects/demo-brand audience-v1 \
  --by "Demo operator" --authorization "Explicit acceptance for a synthetic local demonstration"
```

This records a declaration of authorization, not an authenticated approval.

Create a run and a portable context package:

```bash
python3 -m mos plan projects/demo-brand --workflow campaign-launch \
  --id first-campaign --objective "Prepare a campaign brief and launch readiness review"

python3 -m mos export --workflow campaign-launch --out exports/campaign.md \
  --project projects/demo-brand --memory-id audience-v1
```

Upload the reviewed bundle to the receiving chat and say:

> Use the included Marketing OS workflow for the project in this snapshot. Start by identifying missing information relevant to my request, then execute the necessary role passes. Keep assumptions visible and return proposed memory updates plus a session checkpoint. My request is: …

For a chat that needs the entire library, export `--workflow full` instead. This includes all roles, skills and workflow definitions; it does not instruct the model to run all agents. Prefer a focused bundle when the task is already known. Check the reported size against the receiving model's context limit.

After a role or real agent has actually completed its work, record its handoff:

```bash
python3 -m mos complete-step projects/demo-brand --run first-campaign \
  --step s1 --file examples/handoff.json
```

The handoff example demonstrates structure only. Replace it with the actual result in real work.

## Project second brain

Each project's memory stores evidence, research, brand strategy, offers, decisions, asset references, metrics, learning and session checkpoints. Records carry project scope, sources, versions, status, sensitivity and optional review dates.

New content starts as a proposal. Approved changes preserve prior versions and explicitly supersede competing approved records. Retrieval exposes unresolved alternatives and review dates. A portable export contains only explicitly selected records and refuses to hide competing records for the selected subjects.

Project workspaces are excluded from framework Git. Back up each one privately or use a separate project repository with appropriate access. The reference implementation is local; cloud storage, semantic search and identity-backed approvals are extension points. See [memory protocol](protocols/second-brain.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `START_HERE.md`, `AGENTS.md` | Universal entry point and repository guidance |
| `registry.json` | Versioned agent, skill and workflow catalog |
| `catalog/taxonomy.json` | English taxonomy with stable domain/process/capability IDs |
| `agents/` | Role ownership and handoff boundaries |
| `skills/` | Agent Skills format with focused methods and domain references |
| `protocols/` | Orchestration, second brain and output contracts |
| `workflows/` | Dependency graphs for common marketing initiatives |
| `mos/` | Standard-library CLI for local memory, runs and export |
| `templates/`, `schemas/`, `examples/` | Onboarding, checkpoint, data contracts and synthetic examples |
| `tests/`, `evals/` | Automated invariants and behavioral evaluation scenarios |
| `docs/` | Architecture, portability, extension and release guidance |

## Extension and quality

Follow [EXTENDING.md](docs/EXTENDING.md) to add a specialist, skill, workflow or integration. Use semantic versions; preserve IDs; record breaking migrations. Active runs pin their definitions so an update cannot silently alter a run in progress.

Automated tests validate state, isolation, conflict handling, export and dependency rules. Behavioral scenarios in `evals/` must also be reviewed in the intended AI host before claiming a production integration. Structural tests cannot establish marketing judgment or universal model reliability.

Skill packaging follows [Agent Skills](https://agentskills.io/specification). Repository guidance uses [AGENTS.md](https://agents.md/). These formats support portability; host implementations still differ.

This repository is currently private. No open-source redistribution license has been selected.
