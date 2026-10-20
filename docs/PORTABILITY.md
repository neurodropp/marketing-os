# Host portability

The primary interface is a persistent brand folder, created with `workspace-init`. The user talks to the AI host; the host reads and writes the workspace. A Markdown file alone is not the project memory or an agent execution engine.

| Host | Entry point | Setup |
| --- | --- | --- |
| Codex | AGENTS.md → START_HERE.md | Open the brand folder and request guided setup. |
| Claude Code | CLAUDE.md → START_HERE.md | Start Claude Code in the brand folder and request guided setup. |
| Claude Cowork | Explicit START_HERE.md instruction | Select the brand folder, ask Cowork to read START_HERE.md and retain that instruction in folder instructions. COWORK.md is guidance, not assumed automatic discovery. |

The wrappers route to the same local onboarding protocol, registry, specialist profiles, skills and second brain. Skills are loaded from the registry as files; this release does not install host-native slash commands or named subagent configurations. Actual delegation depends on host features, permissions and user authorization. Sequential role passes are labeled as such.

Python 3.10+ is required for validated state operations. Verify shell, file and Python access in the actual environment. If unavailable, the agent can collect a sourced draft in onboarding/intake-draft.md and report that validated setup is pending. Do not pretend that the utility ran.

## Capabilities and permissions

Declared project capabilities do not grant access. Check actual tools independently. Native host memory may supplement the local second brain but cannot replace it. Move the whole workspace to switch hosts; do not rely on conversation history or hidden host-specific memory. Only load relevant files to manage context size.

## Secondary chat export

`python3 -m mos export --workflow ID --out FILE` remains available for a snapshot without file access. It is a secondary interoperability feature. It cannot supply automatic write-back, durable cross-session memory or independent agents.

## Sources and verification

Host entry-point design was checked against official documentation on 2026-10-20:

- [Codex project instructions](https://developers.openai.com/codex/guides/agents-md)
- [Claude Code project memory](https://code.claude.com/docs/en/memory)
- [Claude Cowork setup](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)

Local tests verify portable folder creation, relocation, registry validation, onboarding persistence, confirmation and project isolation. End-to-end interactive interviews in all three products have not been certified. Instructions guide model behavior; deterministic utilities validate the persisted state they receive, not the truth of a user answer or the quality of marketing judgment.
