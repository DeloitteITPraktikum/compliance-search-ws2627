# 0004: Copilot reads Jira and GitHub through MCP servers

- Status: Proposed
- Date: 2026-11-07
- Owner: EliasGodschalk

## Context

We plan our work in the Jira project DEL and write code with GitHub Copilot in VS Code. Copilot should know what a ticket asks for, without us copying the ticket text into the chat.
Jira will not get the GitHub for Atlassian integration: the Jira admin decided against it. Anything that connects the two has to come from our side.
Copilot changing tickets, issues or pull requests on its own would be risky: a wrong transition, comment or merge is visible to the whole team.

## Decision

The workspace file `.vscode/mcp.json` connects Copilot to the Atlassian MCP server and the GitHub MCP server. Copilot may only read Jira and GitHub: `AGENTS.md` forbids every write tool on both.
Code changes stay in the local workspace; a team member commits, pushes and opens pull requests.

## Alternatives

| Option | Why not |
|---|---|
| A scoped API token with read scopes only | Needs a Jira admin to allow token sign-in for the MCP server; not set up yet |
| A custom agent that lists only the read tools | Only applies when someone picks that agent; the default agent mode still has every tool |
| Letting Copilot write to Jira | Mistakes would land directly in the shared board |
| Letting Copilot write to GitHub (issues, comments, pull requests) | Mistakes would land directly in the shared repository; code reaches it through our own commits anyway |

## Consequences

Copilot can look up tickets, their acceptance criteria, issues and pull requests while we work, and prompt files can build on that. Each team member signs in with their own Atlassian and GitHub account.
The connection to our Jira site (tuda.atlassian.net) is tested.
The read-only rule is an instruction, not a lock: the write tools stay available, and the account's own Jira and GitHub rights apply. Keep VS Code's confirmation before each tool call switched on, and do not auto-approve the Atlassian or GitHub tools.
