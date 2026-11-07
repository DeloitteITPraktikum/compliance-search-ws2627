---
name: start-ticket
description: Liest ein Jira-Ticket über den Atlassian-MCP und fasst zusammen, was zu tun ist, bevor die Arbeit daran beginnt.
argument-hint: Ticket-Key, z. B. DEL-46 (leer lassen, um ihn aus dem Branch-Namen zu nehmen)
agent: agent
tools: ['search', 'read', 'runCommands', 'atlassian/getJiraIssue', 'atlassian/searchJiraIssuesUsingJql']
---
Du hilfst mir, mit der Arbeit an einem Jira-Ticket anzufangen.
Jira liest du nur. Halte dich an die Jira-Regeln in [AGENTS.md](../../AGENTS.md).

## 1. Ticket finden

- Hab ich einen Ticket-Key angegeben (z. B. `DEL-46`), nimm den.
- Sonst lies den Branch-Namen mit `git branch --show-current`. Er beginnt nach [ADR 0003](../../docs/decisions/) mit dem Key, z. B. `DEL-46-mcp-jira-github`.
- Findest du keinen Key, frag mich danach. Rate nicht.

## 2. Ticket lesen

Lies das Ticket aus dem Jira-Projekt DEL: Titel, Beschreibung, Akzeptanzkriterien, Status, Zuständige Person, Kommentare und verlinkte Tickets.

## 3. Zusammenfassen

Antworte kurz auf Deutsch:

1. **Ziel:** Was soll am Ende stehen, in ein bis zwei Sätzen.
2. **Akzeptanzkriterien:** als Checkliste. Hat das Ticket keine, schreib das und schlag welche vor, klar als Vorschlag markiert.
3. **Betroffene Stellen im Repo:** Ordner und Dateien, die wahrscheinlich dazugehören.
4. **Erste Schritte:** drei bis fünf konkrete Schritte.
5. **Offene Fragen:** Was im Ticket unklar ist oder fehlt.

Ändere nichts im Repo und nichts in Jira. Fehlt im Ticket etwas, schlag mir vor, was ich in Jira ergänzen sollte.
