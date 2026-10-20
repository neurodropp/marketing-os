# Orchestration protocol

The orchestrator owns intake, decomposition, routing, dependencies, synthesis and completion. Domain agents own bounded expertise. The reviewer checks acceptance and evidence. The memory steward owns retrieval and proposed memory changes. Strategy approval remains with the authorized project decision maker.

## Intake and routing

Capture project ID, desired deliverable, audience, scope, output language, deadline, constraints and acceptance criteria. Retrieve context before asking questions already answered by approved memory. Ask for missing facts only when they change the work; label provisional assumptions when safe.

For a narrow request, select one domain skill and a proportional review. For broader work, select one of the workflow definitions or construct a work order with an explicit dependency graph. The `route` CLI supplies lexical hints, not semantic classification. Frameworks such as PAS are methods inside content production, not standalone marketing departments.

## Work distribution

Each work order includes project ID, objective, agent ID, skill IDs and versions, source memory IDs/versions, required output, dependencies, available tools and scoped action authorization. Delegation is available only if the host actually supports it and permits it for the task. Parallelize independent work; serialize conflicting writes and dependent decisions. In a single chat, execute role passes sequentially and label them honestly.

Workers return proposals and handoffs. The orchestrator is the single writer of run state; the memory steward serializes memory proposals. No worker may silently overwrite approved strategy. A dependency is satisfied only by an accepted handoff, not by the fact that an agent was started.

## Review and revision

Check evidence, brand consistency, offer/segment fit, deliverable usability and work-order acceptance. For analytics, inspect denominators, time windows and causal claims. For execution, verify tool results and authorization rather than trusting a statement of success.

A review returns pass, revise or blocked with reasons. Use at most the project's configured revision cycles before escalating an unresolved decision; do not loop forever or downgrade acceptance to achieve completion. In the reference CLI, a rejected review blocks the run. A revision creates a new run with a linked prior run ID in its objective and explicit carry-forward evidence; it does not erase history.

## Synthesis and completion

Resolve disagreement by checking evidence quality, approved strategy and the requested outcome. If two plausible options remain, present the trade-off for a decision instead of inventing consensus.

Complete only when the output meets its contract, limitations are disclosed, memory proposals are recorded, and the checkpoint says what is done and what remains. A workflow named “campaign launch” produces launch readiness unless an actual authorized tool action is available and performed.

## Version pinning

The local run utility pins the exact selected agents, skills, references and workflow by content hash. If those definitions change, the run must be explicitly migrated or replaced. Cross-chat continuation also needs the project snapshot, current run, selected skill versions and unresolved decisions; a repository URL alone contains no project memory.

The reference utility also pins the complete active approved-memory set for the project at run creation. If that set changes, it requires context reconciliation and a replacement run. New unapproved proposals do not invalidate the run. This conservative rule can later be refined to explicit per-run memory dependencies in an adapter.
