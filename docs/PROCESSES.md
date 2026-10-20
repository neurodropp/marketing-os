# Operating any of the 108 processes

Every process now has its own English SOP, not just a catalog entry. The source of truth is catalog/processes.json. Rendered procedures live inside the owning skill under references/processes/; stable process and capability IDs are unchanged.

Each SOP contains: trigger and scope, required inputs, five capability-specific operating steps, a concrete output specification and folder, three process-specific quality gates, a stop/recovery condition, downstream ownership and memory/checkpoint instructions.

## Agent workflow

The user can say: "Run F1.03 for this brand using the files in inbox" or simply describe the desired outcome. The orchestrator selects the process, binds evidence, performs the steps, writes artifacts and checks acceptance. The user does not need to operate the CLI.

## Operator workflow

From a standalone brand folder:

```bash
python3 mos.py process-list --domain F1
python3 mos.py process-show F1.03
python3 mos.py process-start . --process F1.03 --id economics-review \
  --objective "Review observed cohort economics" --inputs-file onboarding/economics-inputs.json
```

The input file has project_id and inputs using the template returned by process-show. Copy the completion_template returned by process-start into a new local JSON file, fill it using actual artifacts and review results, then run:

```bash
python3 mos.py process-finish . --run economics-review --file reports/economics-completion.json
python3 mos.py process-status . --run economics-review
```

In the framework repository use `python3 -m mos` and an explicit project path instead of `python3 mos.py .`.

The CLI never creates the marketing deliverable on its own. It checks scope, versions, evidence files, gate declarations and completion state. The host supplies reasoning, research, production tools and authorized external execution. Missing inputs/tools lead to a useful draft or a blocked action, not fabricated results.

## Workflow integration

All ten workflows map domain steps to process_ids. Each mapped process must have an accepted ready/executed run. Supply those run IDs in the step handoff's process_runs array. The workflow validates coverage and detects changed evidence, including evidence from earlier accepted steps. Choose a standalone process for narrower work.

## Maintain the library

Edit the corresponding canonical entry in catalog/processes.json; keep the input/step/gate IDs stable when compatible. Update skill and process versions together, regenerate the Markdown with `python3 scripts/render_processes.py`, then run validation and tests. `--check` detects source/render drift in CI. SOPs are complete procedures; platform-specific API commands still require a suitable current connector and explicit authorization.

Existing private workspace snapshots remain pinned to their previous release. Create a new 0.3.0 workspace for new brands. For an existing brand, back it up and explicitly plan the framework migration, preserving its data and previous run history; do not overwrite the folder with a starter ZIP. There is no automatic snapshot migration utility in this release.
