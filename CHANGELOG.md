# Changelog

## 0.3.0 — Complete operational SOP library

- Implement all 108 English SOPs with concrete inputs, five capability-specific steps, output contracts, three process-specific gates, stop/recovery rules and handoffs; preserve all 540 capability IDs.
- Revise all 19 agent profiles and 19 skills with precise routing, ownership boundaries, selective context loading, evidence review and persistence rules.
- Add a canonical process catalog, readable index, deterministic renderer and CI drift checks.
- Add process-list/show/start/finish/status, pinned input/context evidence, artifact hashes and draft/ready/executed states.
- Bind all ten workflows to required process runs; reject missing, stale, modified or draft process evidence.
- Add 15 tests (50 total), including a 108-process contract round trip, and four reproducible authored reference cases. Define 95 target-host behavioral cases without claiming they have all run.
- Document current primary engineering/domain sources and remaining live-integration limits.

### Compatibility

Taxonomy, memory IDs and schemas are preserved. New workflow runs require process_runs on mapped domain handoffs. Previous source definitions remain pinned in existing workspaces; moving to this release requires explicit reconciliation and replacement of affected runs, not silent repointing. No private workspace is automatically upgraded or overwritten.

## 0.2.0 — Folder workspaces and guided onboarding

- Add standalone brand folders with a private, relocatable framework snapshot.
- Add Codex and Claude Code entry points and explicit Cowork folder instructions.
- Add six-stage, resumable brand intake with sourced answers, optional deferrals, revision checks and digest-bound user confirmation.
- Preserve answer history; corrections invalidate confirmation, while assumptions retain their status.
- Make folder-based operation primary and chat export secondary.
- Add seven deterministic tests (35 total); cross-host interactive behavior still requires evaluation.

## 0.1.0

- Initial portable architecture with 16 marketing domains and three control roles.
- Nineteen focused skills with local domain references.
- English catalog preserving 108 process and 540 capability identifiers.
- Ten dependency-aware workflows and structured handoff contracts.
- Local project second brain with proposals, sources, immutable versions, explicit supersession and conflict visibility.
- Standard-library CLI for validation, initialization, memory, run planning, handoffs and context export.
- Automated invariant tests and a separate host behavioral evaluation pack.

This is a reference implementation. Native SDK orchestration, cloud memory, authenticated approvals and live marketing connectors are future optional adapters.
