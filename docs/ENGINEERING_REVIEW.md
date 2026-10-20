# Agent and skill engineering review — 0.3.0

Reviewed 2026-10-20. This is a documented engineering revision, not a claim of benchmark superiority or universal host certification.

## Changes applied to all 19 roles and skills

- Domain descriptions identify the requested output and neighboring ownership boundaries. Control roles have explicit coordination, memory and review responsibilities.
- Each domain skill provides direct links to its SOPs plus a small index; individual SOPs load on demand. The registry still preserves all 16 domains, 108 processes and 540 capability IDs.
- Work orders bind input evidence and pin the selected definitions, approved memory and intake. Completed artifacts and review evidence are hashed for change detection.
- Process gates distinguish draft, ready and externally executed work. Review examines artifacts and evidence rather than accepting completion prose alone.
- One writer integrates shared state. Delegation is conditional on real host support and authorization; a sequential role pass is never described as independent review.
- Revision limits, missing-tool behavior, reconciliation and recovery are explicit. No agent can self-authorize a purchase, publication or strategy change.
- Tests exercise state invariants and all 108 process contracts. Behavioral evaluation cases remain distinct from deterministic tests.

## Primary guidance consulted

[OpenAI skill guidance](https://developers.openai.com/codex/skills) and the [Agent Skills specification](https://agentskills.io/specification) support concise discovery metadata and loading detailed references only when relevant. This repository uses short skill entry points, direct SOP references and self-contained skill resource folders.

[Anthropic's agent architecture guidance](https://www.anthropic.com/engineering/building-effective-agents) supports choosing complexity according to the task. Its original article explicitly notes that tooling has evolved. This project adopts the enduring design principle of bounded, composable work; it does not copy old SDK configurations or imply a managed-agent integration.

[Anthropic's evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) distinguishes final environment outcomes from what an agent says happened. Here, filesystem artifacts, evidence hashes, process status and action receipts are checked separately from model prose. Structural checks cannot determine marketing quality or authenticate an approver.

## Domain references and freshness

These references informed specific review concerns; the 108 SOPs are original operational instructions, not copied vendor manuals.

- [Google Search content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): useful content, clear sourcing and audience task completion in O2.01/O2.05/O3.01.
- [Google Analytics reporting identity](https://support.google.com/analytics/answer/10976610): identity and measurement scope must be explicit in F7.04/G1 processes. No cross-device completeness is assumed.
- [WCAG quick reference](https://www.w3.org/WAI/WCAG22/quickref/): check relevant accessibility criteria against actual artifacts in F3.04/F6.07/O4.01/G2.05. A checklist is not accessibility certification.
- [Gmail sender guidance](https://support.google.com/mail/answer/81126): current provider requirements should be checked before email delivery in O3.04/O6.02. Exact thresholds and platform settings are intentionally verified at execution time rather than frozen into generic SOPs.
- [Microsoft experimentation research](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/): further primary research for experiment validity and interpretation. G2 requires a stated design and decision rule rather than treating early metric movement as a winner.

Platform UI, APIs, placement specifications, deliverability thresholds, prices and legal requirements can change. The operating agent must verify current official sources when a task depends on them and record the source/date. This release does not promise permanently current platform mechanics.

## Explicit limits

No new model API, third-party account access, paid service, native named-agent installation or autonomous publishing was introduced. The host AI executes the procedures with its available tools. An input status, review verdict or authorization reference is an auditable declaration, not authenticated proof. Cross-host end-to-end behavioral testing remains separate from the local suite.
