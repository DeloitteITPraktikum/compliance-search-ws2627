---
name: pr-description
description: Schreibt die Beschreibung für einen Pull Request aus dem Jira-Ticket des Branches und den Änderungen gegenüber main.
argument-hint: Ticket-Key, z. B. DEL-46 (leer lassen, um ihn aus dem Branch-Namen zu nehmen)
agent: agent
tools: ['search', 'read', 'runCommands', 'atlassian/getJiraIssue']
---
Du schreibst mir die Beschreibung für den Pull Request des aktuellen Branches.
Jira liest du nur. Halte dich an die Jira-Regeln in [AGENTS.md](../../AGENTS.md).

## 1. Material sammeln

- **Ticket-Key:** den angegebenen, sonst aus `git branch --show-current`. Findest du keinen, frag mich.
- **Ticket:** Lies Titel, Beschreibung und Akzeptanzkriterien aus Jira.
- **Änderungen:** `git log --oneline origin/main..HEAD` und `git diff origin/main...HEAD`. Gibt es noch nicht committete Änderungen, weise mich darauf hin, dass sie nicht im Pull Request landen.
- **Vorlage:** [.github/pull_request_template.md](../pull_request_template.md)

Führe nur lesende Git-Befehle aus.

## 2. Beschreibung schreiben

- **Titel:** `<Ticket-Key>: <was sich ändert>`, z. B. `DEL-46: MCP-Anbindung an Jira und GitHub`.
- **Text:** genau die Abschnitte der Vorlage, in derselben Reihenfolge. Sprache wie die übrigen Docs: Englisch.
  - Die Jira-Zeile bekommt den Link auf das Ticket.
  - `What changes`: was der Pull Request ändert, nicht wie. Zwei bis vier Sätze.
  - `How I tested it`: nur, was im Diff, in den Commits oder von mir belegt ist. Fehlt etwas, schreib einen Platzhalter und sag es mir.
  - Checkliste: Hak nichts ab, was du nicht geprüft hast.
- **Abgleich:** Liste darunter getrennt auf, welche Akzeptanzkriterien des Tickets der Diff erfüllt und welche noch offen sind.

Gib Titel und Text als Markdown im Chat aus. Leg den Pull Request nicht selbst an und ändere nichts in Jira.
