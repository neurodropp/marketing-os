# Marketing OS

A portable agentic framework for marketing and brand projects, with a durable second brain for each project.

The framework combines **16 marketing domains, 108 processes and 540 capabilities** with **19 agent roles and 19 modular skills**: an orchestrator, 16 domain specialists, a memory steward and a quality reviewer. Domain coverage is a planning taxonomy; it is not 540 fully implemented automations.

The repository is in English. Project deliverables can use the project's configured language.

## What you can use today

- Run a marketing assignment through documented agent roles and focused skills.
- Start a private project workspace with versioned memory, sources, approvals and conflicts.
- Use ten dependency-aware workflows: brand foundation, campaigns, offers, content, reputation, tracking incidents, retention, lifecycle, performance and strategic reviews.
- Guide users through resumable brand setup and save deliverables in a standalone folder.
- Validate registry references and workflow dependencies, pin a run to exact skill definitions, and record accepted handoffs.
- Add or update skills, agents and workflows without changing the core project memory.

The Python utilities perform local state management. They do **not** call an LLM, spawn agents, authenticate users, publish content, spend money or connect accounts. The host AI environment supplies those capabilities where available.

## Start in Codex, Claude Code or Cowork

Open this repository in your AI host and ask:

> Create a brand workspace and guide me through setup. Save everything in the project folder so we can resume later.

The agent asks for the brand name and folder destination, then guides you through six short stages: identity, objectives, audience and offer, brand direction, resources, and materials. Answers are saved after each reply. Unknowns can remain open; the final summary is confirmed before setup is marked complete.

For Codex, the entry point is `AGENTS.md`; for Claude Code it is `CLAUDE.md`. In Cowork, select the folder and explicitly ask it to read `START_HERE.md`; retain that instruction in folder instructions. See [host setup](docs/PORTABILITY.md).

## Folder quick start

The AI can run these commands for you. Python **3.10+** is required; no third-party packages are needed.

```bash
git clone https://github.com/neurodropp/marketing-os.git
cd marketing-os
python3 -m mos workspace-init ../my-brand --id my-brand --brand "My Brand"
```

Open the new `my-brand` folder and ask the agent to read `START_HERE.md` and begin onboarding. It includes its own framework snapshot, agent profiles, skills, local utilities, working folders and second brain. Moving the whole folder preserves the project.

```text
my-brand/
  AGENTS.md / CLAUDE.md / COWORK.md / START_HERE.md
  .marketing-os/             Framework snapshot, agents and skills
  onboarding/               Resumable setup and answer history
  inbox/                    Source materials
  brand/ research/ strategy/
  campaigns/ content/ reports/ decisions/
  memory/records/           Versioned knowledge and decisions
  memory/sessions/          Session checkpoints
  runs/                     Workflow progress
```

The onboarding is conducted by the host AI, with local utilities enforcing state consistency. The user does not have to edit JSON. See [workspace behavior and lifecycle](docs/WORKSPACES.md).

From the brand folder, `python3 mos.py --help` exposes onboarding, memory and workflow commands. `python3 -m mos init` remains available from the framework for a minimal data-only project. Markdown export is retained as a secondary fallback for environments without folder access.

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
