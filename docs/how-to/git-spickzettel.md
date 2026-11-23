# Spickzettel: Git, GitHub und uv

Die Befehle aus dem [Workshop](../tutorials/git-uv-workshop.md) zum Nachschlagen.

## Der Ablauf für jedes Ticket

| Schritt | Terminal | VS Code |
|---|---|---|
| 1. Neuesten Stand holen | `git switch main`, dann `git pull` | Branch unten links anklicken, `main` wählen, dann Sync |
| 2. Branch anlegen | `git switch -c DEL-12-kurzes-thema` | Branch unten links, „Create new branch“ |
| 3. Ändern und ansehen | `git status`, `git diff` | Source Control, Datei anklicken |
| 4. Auswählen (stagen) | `git add <datei>` | Plus neben der Datei |
| 5. Speicherpunkt (Commit) | `git commit -m "Was sich ändert"` | Nachricht schreiben, Commit |
| 6. Hochladen | erstes Mal `git push -u origin <branch>`, danach `git push` | Publish Branch, danach Sync |
| 7. Pull Request | auf GitHub: Compare & pull request | |
| 8. Review | zweite Person: Files changed, Review changes, Approve | |
| 9. Merge | auf GitHub: Merge pull request, Delete branch | |
| 10. Aufräumen | `git switch main`, dann `git pull` | `main` wählen, Sync |

Schritte 3 bis 6 beliebig oft. Jeder neue Push landet im selben Pull Request.

Regeln: ein Ticket, ein Branch, ein Pull Request. Kein Push auf `main`. Titel des Pull Requests beginnt mit dem Ticket, z. B. `DEL-12: Add POST /ask`.

## uv

| Ich will | Befehl |
|---|---|
| Ein Skript in `setup/` starten | `uv run --env-file .env check.py` |
| Die Tests starten (in `backend/`) | `uv run pytest` |
| Den Server starten (in `backend/`) | `uv run uvicorn compliance_search.api.app:app --port 8000` |
| Den Server stoppen | Ctrl + C |
| Ein Paket hinzufügen | `uv add <paket>`, dann `pyproject.toml` **und** `uv.lock` committen |
| Die `.venv` auf den Stand von `uv.lock` bringen | `uv sync` |

## Terminal

| Ich will | Befehl |
|---|---|
| Wissen, wo ich bin | `pwd` |
| Sehen, was hier liegt | `ls`, mit versteckten Dateien `ls -a` (Windows: `ls -Force`) |
| In einen Ordner gehen | `cd setup` |
| Eine Ebene hoch | `cd ..` |
| Namen ergänzen, letzten Befehl holen | Tab, Pfeil nach oben |

## Was mache ich, wenn …

| Situation | Lösung |
|---|---|
| Ich weiß nicht, auf welchem Branch ich bin | `git status`, oder unten links in VS Code |
| Ich habe auf `main` geändert, noch nicht committet | `git switch -c DEL-12-thema`, die Änderung kommt mit |
| Ich habe auf `main` committet, noch nicht gepusht | `git switch -c DEL-12-thema`, dann `git branch -f main origin/main` |
| Ich will eine Änderung verwerfen | Source Control, Pfeil zurück (Discard Changes). Weg ist weg |
| Der letzte Commit war falsch, noch nicht gepusht | Source Control, …, Commit, Undo Last Commit |
| Der falsche Commit ist schon gepusht | Neuer Commit mit der Korrektur, pushen |
| Der Fehler ist schon in `main` | Auf GitHub im gemergten Pull Request: Revert |
| GitHub meldet „This branch has conflicts“ | Auf deinem Branch `git pull origin main`, Stelle in VS Code auflösen, die Zeilen `<<<<<<<`, `=======`, `>>>>>>>` entfernen, stagen, committen, pushen |
| `git pull` meldet „Need to specify how to reconcile divergent branches“ | Einmalig `git config --global pull.rebase false` |
| `git push` meldet „has no upstream branch“ | `git push -u origin <branch>` oder Publish Branch |
| `uv: command not found` | Neues Terminal öffnen |
| `GATEWAY_KEY is missing` | `--env-file .env` fehlt, oder du bist nicht in `setup/` |
| `ModuleNotFoundError` | Mit `uv run` starten, nicht mit `python` |
| `Address already in use` | Der Server läuft noch in einem anderen Terminal: dort Ctrl + C |

Im Zweifel zuerst `git status`. Es sagt, wo du bist und was Git gerade sieht.
