# Process execution protocol

Every taxonomy process has a canonical contract in catalog/processes.json and a readable SOP in its owning skill's references/processes folder. The agent reads only selected SOPs. A process is an executable instruction procedure for the host AI and operator; the Python CLI supplies deterministic state/evidence checks, not an autonomous marketing integration.

## Work order

1. Read the project's confirmed intake, relevant memory and current request.
2. Use `process-show ID` to retrieve inputs, steps, output and gates.
3. Create an inputs payload with project_id and inputs keyed by the exact i1/i2/... IDs. Each binding contains status (provided, unknown, not-applicable), references (project-relative local file paths) and a nonempty note. Capture remote evidence in a local source note with URL, access date and limitations; the CLI does not fetch URLs.
4. Start a process run. It pins the selected SOP, skill, agent, execution protocols, source files, approved memory and intake. Treat pinned input files as immutable: corrections require a replacement run.
5. Follow the SOP with actual host tools, save outputs in its prescribed folder and inspect the artifacts. Record calculations and tool evidence where the result depends on them.

A missing input can support a draft or a collection plan. Mark not-applicable only with a task-specific reason, not to bypass missing evidence. The CLI validates these declarations structurally; the reviewer assesses whether they are justified.

## Completion

`process-start` returns the completion template. Fill every field and call `process-finish`.

- **draft:** useful local artifacts exist, but one or more inputs/checks may remain unresolved. State limitations and next action.
- **ready:** every quality gate passes with a local evidence file, required input statuses are resolved and the requested local deliverable is usable.
- **executed:** ready conditions hold and external actions have receipts naming the target, exact effect, authorization reference, observed result and local evidence file.

Local production itself normally ends ready. Do not invent an external action to label a local report executed. An action receipt is not an authentication mechanism. A model can still make false declarations; reviewers must inspect artifacts and evidence rather than relying on the CLI to establish truth.

The completion payload also records reviewer identity, role-pass/delegated mode, review summary, limitations, memory proposal references and next action. Actual delegation is possible only when the host supports and authorizes it; a project capability flag is a declaration, not proof.

Completion pins artifact and evidence contents. `process-status` detects subsequent changes, including changes to inputs, definitions, approved memory or intake. Preserve previous runs and create a replacement run for revisions; include the prior run ID in the objective and checkpoint. The orchestrator enforces the project revision budget. No history is silently erased.

## Multi-process workflows

Workflow steps name their required process IDs. Run each mapped process through its own work order and supply the resulting run IDs in the workflow handoff's `process_runs` array. The workflow utility verifies exact process coverage, ready/executed status, current source/definition/memory hashes and intact artifacts before accepting the step. It rechecks previously accepted process evidence on later handoffs.

For a narrower request, use a standalone process or a deliberately scoped custom workflow instead of bypassing mapped processes. Control steps (memory and review) do not require domain process runs. Pre-0.3.0 runs retain their old structure but changed pinned definitions require reconciliation and a replacement run.
A selected process with a failed/unverified gate cannot be represented as ready in the workflow handoff. Keep external effects separate from preparation. A launch workflow can correctly finish with a readiness package while publication remains unexecuted.

## Failure and recovery

Missing tools: deliver a specification, draft or test plan and name the unperformed operation. Unknown critical facts: record the gap and its decision impact. External tool failure: inspect actual state before retrying a potentially duplicate operation. Conflicting approved memory: preserve both and obtain the necessary decision. File lock: inspect the active writer before removing a stale lock. No infinite retry loops or acceptance downgrades.
