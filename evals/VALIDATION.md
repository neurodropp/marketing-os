# Validation record — 0.3.0

Date: 2026-10-20.

## Completed locally

- Registry: 19 agents, 19 skills, 16 domains, 108 operational SOPs, 108 distinct procedures, 540 preserved capability IDs and 10 workflows.
- 324 process-specific quality gates; each SOP also has input readiness, output, recovery and handoff requirements.
- All 19 skill packages passed the skill-creator structural validator.
- All 50 automated tests passed. One test loops through all 108 process contracts for start, finish and resume using explicitly synthetic state-machine fixtures. This is contract coverage, not 108 successful real marketing engagements.
- Tests reject missing/misaligned SOP coverage, missing workflow mappings, stale inputs, changed intake or approved memory, missing/failed gates, changed artifacts, cross-project evidence, symlinks, missing external-action receipts and unbacked workflow completion.
- Generated SOPs match their canonical source; source Markdown links and Git whitespace checks passed.
- Four authored reference scenarios ran through the actual process utility: observed unit economics (ready), research without participants (draft), paid social without account/spend/tracking readiness (draft), and experiment design without baseline/traffic (draft).
- Economics assertions: CAC EUR 140; observed three-month contribution EUR 189 per initial customer; first observed payback at month three; downside contribution EUR 162 does not cover CAC EUR 180. No lifetime value, causal research result or live campaign is invented.

The reproducible runner is scripts/run_synthetic_smoke.py. Its outputs are included under examples/reference-smoke/. These are authored examples and a role-pass review, not independent model trials.

## Defined, not claimed executed

The 95 cases in skill-cases.json cover positive use, adjacent routing, missing input, contradictory memory and missing tools for each of the 19 skills. They remain explicitly marked not run in target hosts. Full interactive evaluation across Codex, Claude Code and Cowork, live accounts, real participant research and independent expert review remain outside the completed local checks.

No benchmark superiority, universal production readiness, legal compliance or authenticated approval is claimed. The CLI checks structure, file existence and changes; an operator still verifies the truth and quality of evidence.

## Previous release records

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
