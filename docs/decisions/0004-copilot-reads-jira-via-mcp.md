# 0004: Copilot reads Jira through the Atlassian MCP server

- Status: Proposed
- Date: 2026-11-07
- Owner: EliasGodschalk

## Context

We plan our work in the Jira project DEL and write code with GitHub Copilot in VS Code. Copilot should know what a ticket asks for, without us copying the ticket text into the chat.
Jira will not get the GitHub for Atlassian integration: the Jira admin decided against it. Anything that connects the two has to come from our side.
Copilot changing tickets on its own would be risky: a wrong transition or comment is visible to the whole team.

## Decision

The workspace file `.vscode/mcp.json` connects Copilot to the Atlassian MCP server (and the GitHub MCP server). Copilot may only read Jira: `AGENTS.md` forbids every write tool.

## Alternatives

| Option | Why not |
|---|---|
| A scoped API token with read scopes only | Needs a Jira admin to allow token sign-in for the MCP server; not set up yet |
| A custom agent that lists only the read tools | Only applies when someone picks that agent; the default agent mode still has every tool |
| Letting Copilot write to Jira | Mistakes would land directly in the shared board |

## Consequences

Copilot can look up tickets and their acceptance criteria while we work, and prompt files can build on that. Each team member signs in with their own Atlassian account.
The read-only rule is an instruction, not a lock: the write tools stay available, and the account's own Jira rights apply. Keep VS Code's confirmation before each tool call switched on, and do not auto-approve the Atlassian tools.
