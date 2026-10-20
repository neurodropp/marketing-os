# Folder workspaces and guided setup

Open the framework repository in your AI host and say:

> Create a new brand workspace and guide me through initial setup. Save answers and work in its folders, and resume from there next time.

The agent collects the brand name and destination, creates the workspace, and interviews you in short blocks. No terminal or JSON editing is required from the user when the host can run local Python tools.

## Local utility

For an operator who prefers a terminal:

```bash
python3 -m mos workspace-init ../my-brand --id my-brand --brand "My Brand"
```

Then open `../my-brand` in your AI host. The folder contains its own copy of the framework and does not depend on the original checkout's location.

```text
my-brand/
  AGENTS.md                 Codex entry point
  CLAUDE.md                 Claude Code entry point
  COWORK.md                 Explicit Cowork setup instructions
  START_HERE.md             Shared session procedure
  project.json              Stable project ID and declared runtime configuration
  mos.py                    Local utility entry point
  .marketing-os/            Framework, specialist profiles, skills and workflows
  onboarding/state.json     Created when the first answers are saved
  inbox/                    Existing documents and evidence
  brand/                    Brand brief, voice and setup summaries
  research/                 Research outputs
  strategy/                 Strategy deliverables
  campaigns/                Campaign work
  content/                  Content deliverables
  reports/                  Analysis and reporting
  decisions/                Human-readable decision documents
  memory/records/           Versioned canonical decision and knowledge records
  memory/sessions/          Durable session checkpoints
  runs/                     Workflow state and handoffs
```

Each brand gets a separate folder. Source framework updates do not mutate existing workspace snapshots. Keep custom framework changes in a separate versioned source checkout and follow EXTENDING.md. There is currently no automated in-place snapshot migration: preserve the current snapshot for active runs and plan any upgrade explicitly with backup and hash validation. Never copy a release over private data or assume an old run can silently adopt changed definitions.

## Setup lifecycle

Six short stages cover identity, objectives, audience/offer, brand, operations and materials. The source of truth is `onboarding/state.json`; summaries in brand/ are views with a revision and digest. The CLI checks project scope, required answers, stale writes and confirmation of the precise answer set. Changes preserve prior answers and invalidate confirmation.

Users can defer optional questions and continue useful work. Four fields need stated answers to finish: brand name, output language, first priority and first task. Existing marketing workspaces created with `init` can use onboarding commands without recreating memory. `init` remains the minimal data-only command; `workspace-init` is the standalone folder command.

The six stages and response contract are defined in `mos/onboarding.py`; the agent interview procedure is in `protocols/onboarding.md`. A deterministic helper returns the next block; the host AI conducts the interview and writes readable summaries. There is no separate graphical wizard and the CLI does not itself call an AI model.

## Resume and privacy

At every session start, the agent reads onboarding status, relevant memory and the latest checkpoint. It must save replies before moving to the next stage. Onboarding sources can reference user replies or supplied documents. Confirmed intake remains user-provided background; hypotheses are not facts and intake does not silently supersede approved strategic memory.

Back up the whole brand folder privately. Workspaces under this repository's projects/ are ignored by Git; destinations elsewhere require their own private backup/access policy. Neither setup nor a declared budget authorizes external publishing, account connection or spending.
