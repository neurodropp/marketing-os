# Extending and updating Marketing OS

## Add a skill

Create `skills/<lowercase-hyphen-name>/SKILL.md` with YAML `name`, `description` and `metadata.version`. Keep its method focused on the output and meaningful decision criteria. Add any detailed resources within that skill's `references/`, `scripts/` or `assets/` directory. Do not create empty scaffolding.

Register its ID, version, path, owning agent, domain (or null), description, discovery keywords and reference paths in registry.json. Add the skill ID to the owning agent. One role may own several skills. Add realistic routing and behavior cases to evals/.

## Add an agent

Define a bounded responsibility, inputs, output contract, expertise boundary and escalation path in `agents/<id>.md`. Register it and assign skills. Reuse existing marketing domains unless the discipline model genuinely requires a new one. New roles do not require running more agents on every task.

## Add a workflow

Create a JSON graph with stable step IDs, known agent IDs, explicit dependencies and an output per step. Register its path. Keep independent steps parallelizable, but never permit simultaneous conflicting writes to the second brain. `python3 -m mos validate` rejects missing references and cycles.

## Update an existing component

Use semantic versions: patch for a compatible correction, minor for added compatible capability, major for contract changes. Update the registry and skill frontmatter together. Record changes in CHANGELOG.md.

Existing runs pin exact content, including agent profiles and references. They stop if definitions change. Continue on the previous repository revision, start a replacement run carrying prior evidence, or implement and document an explicit migration. Never silently repoint active runs.

## Evolve memory

Preserve record IDs, sources, timestamps and history. A new interpretation becomes a proposal. New accepted strategy explicitly supersedes prior approved strategy of the same kind and subject. Schema changes require a migration with backup, dry run, validation and rollback instructions. Unknown schema versions are refused by the reference utility.

## Add a connector or memory backend

Keep it optional. Specify required capability, credentials source, project boundary, read/write effects, authorization rules, idempotency, rate limits and failure behavior. Secrets live in the host's credential store, not project prompts. An indexed or remote memory backend must pass the same isolation/conflict/history tests as local storage.

## Acceptance before release

Run repository validation and unit tests. Evaluate at least one positive use, one adjacent request that should route elsewhere, a missing-input case, a contradictory-memory case, and a tool-unavailable case. Record actual host results separately from deterministic test results. Test external effects only in an authorized sandbox.

Review changes before Git commit. Do not package project workspaces, user attachments, customer records or credentials in a framework release.

## Learning without silent framework mutation

Repeated project failures or successful techniques may justify a skill improvement. Store the observation as project learning first. Propose a framework change with the reusable lesson, supporting cases, affected skills and an evaluation plan. Remove private brand details before promoting the lesson into the shared framework.

Evaluate the proposed change, bump versions and publish a release. A project can choose when to upgrade. Project memory, approved strategy and active runs remain separate from the shared skill catalog; an agent never rewrites its own operating contract during a live run just to make a task pass.

## Maintain operational process contracts

Every taxonomy process must have one catalog/processes.json entry, an owning skill reference and a rendered SOP. Keep the five stable capability IDs mapped to their operating steps. Bind workflow domain steps to process_ids owned by the assigned agent. Their completion requires matching ready/executed process runs; use a smaller custom workflow for smaller scope rather than removing evidence gates.

Update the canonical contract and the skill/process versions together. Render with scripts/render_processes.py, check drift with --check, then run validation, tests and relevant synthetic/behavioral cases. Process gates must describe observable deliverable quality, not merely the presence of a heading. Preserve existing IDs and document any contract change that affects old runs.
