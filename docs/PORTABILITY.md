# Portability and integration

## Portable core

Markdown instructions, JSON contracts and the English taxonomy can be read by any text-capable model with sufficient context. This is instructional portability, not an assurance that every model can execute every workflow correctly.

A private GitHub repository requires authorized access. Pasting its URL into a chat may not load it. Clone it in an authorized environment or generate and upload a reviewed bundle.

## Chat-only mode

Export a selected workflow; include only the project records needed. Upload or paste it into the host. Ask the model to perform labeled role passes. It can draft and reason without tools. It cannot save durable memory, access live sources, publish, or create genuinely independent workers unless the host supplies those functions.

Save the session checkpoint and memory proposals yourself, then reconcile them into the authoritative second brain. Preserve project ID, sources and versions. Do not promote an unverified chat summary into a verified fact.

## File-capable assistant

Open the repository, read START_HERE.md and select a private project workspace. The assistant can use the standard-library CLI if shell execution is available. AGENTS.md is a convenience for hosts that discover it; explicitly reading START_HERE.md remains the fallback.

Skill folders use the Agent Skills structure. Native installation/discovery varies by product. Copying a skill alone carries its method and local references, but not the framework's orchestration or project memory. This repository does not alter global assistant configuration.

## Delegated or SDK runtime

Implement an adapter that:

1. Binds an active project and authenticates tool access.
2. Loads selected role/skill versions and the approved context packet.
3. Creates real workers if supported and authorized.
4. Enforces the dependency graph and action permissions.
5. Receives and reviews structured handoffs.
6. Serializes memory proposals and records authorized decisions.
7. Persists run state, evidence and checkpoint.

The repository supplies contracts and local persistence; a production SDK adapter, background scheduler, vector database, authenticated approvals and connector implementations are not included in this release.

## Capability declaration

Declare actual file, research, delegation and connector access at the start of a session. Settings in project.json are intended configuration, not proof of capability. Missing capabilities produce a useful draft/specification or a clearly scoped blocker. Never claim a connector ran because a workflow names one.

Model context limits and tool APIs vary. Run the behavioral scenarios in the target host and record the model/version, capability mode and observed result before describing an integration as tested.
