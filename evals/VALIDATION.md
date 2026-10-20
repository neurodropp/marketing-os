# Validation record — 0.2.0

Date: 2026-10-20.

- Repository validation passed: 19 agents, 19 skills, 16 domains, 108 processes, 540 capabilities, 10 workflows.
- All 35 local automated tests passed (28 existing plus seven onboarding/workspace tests).
- A standalone workspace was moved to another path; its copied CLI successfully resumed intake and validated the bundled framework.
- Tests cover stale answer revisions, cross-project refusal, symlink refusal, confirmation invalidation, immutable prior answer history, required/optional unknowns, and preservation of assumptions and external permissions.
- Official host documentation was consulted for entry-point design. Interactive setup has not been tested end-to-end in Codex, Claude Code and Cowork; no native host certification is claimed.
- No in-place framework snapshot updater or graphical wizard is included in this release.

## Previous release record

# Validation record — 0.1.0

Date: 2026-10-20.

Completed in the local reference environment:

- Repository graph validated: 19 agents, 19 skills, 16 domains, 108 processes, 540 capabilities, 10 workflows.
- All 19 SKILL.md files passed the skill-creator structural validator.
- 28 automated tests passed, covering project isolation, proposal/approval history, conflicts, supersession, rejection, locked writes, scope checks, workflow dependencies, blocked reviews, definition pinning, memory changes, extension registration and exports.
- A seven-command documented CLI flow passed: initialize, propose memory, accept, retrieve, plan, record a handoff and export.
- All original 108 process identifiers were preserved in the English catalog.
- Source Markdown links were checked for missing local targets.
- Full-library and all ten workflow bundles were generated. The full bundle is approximately 122,000 characters; token counts reported by the CLI are character-based estimates.
- GitHub Actions also passed repository validation, the 28-test suite and context export on Python 3.10 and 3.13. The workflow uses pinned action commits and an explicit Ubuntu runner image.

These checks establish deterministic repository and local-state behavior. They do not establish marketing correctness for every project, adversarial robustness of every model, authenticated approvals, live connector behavior or native integration with every AI product.

The host scenarios in SCENARIOS.md are supplied for behavioral evaluation. No independent multi-model or production connector certification is claimed in this release.
