# Work orders, handoffs and review

## Work order

Provide: project ID; run/step IDs; objective; requested deliverable; domain and skill versions; approved input memory IDs with versions; dependencies; constraints; available tools; authorized actions; acceptance criteria; unresolved facts. Avoid large irrelevant context dumps. A plan is not permission to spend or publish.

## Handoff

The CLI accepts JSON with:

```json
{
  "project_id": "demo-brand",
  "step_id": "s1",
  "execution_mode": "role-pass",
  "deliverable": "Artifact path or substantive result",
  "sources": ["memory:audience-v1@2"],
  "assumptions": [],
  "acceptance": "What was checked and whether the output meets the work order",
  "memory_proposals": []
}
```

Use `delegated` only for a real delegated execution. The reviewer also returns `verdict`: pass, revise or blocked. Source and artifact references must be inspected by the host where the decision depends on them; the CLI checks structure and order, not the truth of prose.

## Review rubric

Evaluate relevance to the request; evidence quality and uncertainty; consistency with approved brand/offer/audience; output usability; operational dependencies; metrics and test validity; permission and execution claims; memory updates and conflicts.

Return specific defects with evidence and a remedy. A self-review in one conversation is a role pass, not independent validation. Structural success from the CLI is never a substitute for substantive review.

## External actions

Before an external action, verify a capable tool, target project/account, exact intended effect and user authorization within the host's rules. Report draft, prepared, attempted and confirmed states accurately. The reference CLI never sends, publishes, purchases, connects an account or calls a model.
