# Workshop: Terminal, uv, Git und GitHub

Am Ende hast du eine eigene Änderung vom Branch bis in `main` gebracht, einen Pull Request geprüft, einen Konflikt gelöst und einen Fehler rückgängig gemacht.

So arbeitest du mit dem Blatt:

- Du arbeitest am eigenen Laptop, im Paar mit deiner Review-Person.
- Jeder Block endet mit einem **Checkpoint**. Stimmt er, geht es weiter. Stimmt er nicht, frag zuerst dein Paar, dann die Runde.
- Wer früher fertig ist, macht den **Bonus** oder hilft nebenan.
- `DEL-44` ist das Workshop-Ticket, `<vorname>` dein Vorname in Kleinbuchstaben.
- Git schreibt seine Meldungen je nach Laptop auf Deutsch oder Englisch. Die Befehle sind dieselben.

Windows: Nimm das Terminal in VS Code (PowerShell). Wo ein Befehl anders heißt, steht es dabei.

---

## Block 0: Ankommen (10 min)

1. Öffne VS Code, dann **File → Open Folder** und wähle den Ordner `compliance-search-ws2627`.
2. Öffne das Terminal in VS Code: **Terminal → New Terminal**.
3. Prüfe die Werkzeuge:

   ```sh
   git --version
   uv --version
   ```

4. Prüfe, wer du für Git bist. Beide Befehle müssen etwas ausgeben:

   ```sh
   git config user.name
   git config user.email
   ```

   Kommt nichts: `git config --global user.name "Dein Name"` und `git config --global user.email "deine@mail"`.

5. Stell einmalig ein, dass `git pull` zusammenführt. Ohne diese Einstellung bricht `git pull` später in Block 5 mit einer Fehlermeldung ab:

   ```sh
   git config --global pull.rebase false
   ```

6. Hol den neuesten Stand:

   ```sh
   git switch main
   git pull
   ```

**Checkpoint:** Unten links in VS Code steht `main`, und `git status` meldet, dass nichts zu committen ist.

---

## Block 1: Terminal und Projekt (15 min)

1. Wo bin ich, was liegt hier?

   ```sh
   pwd
   ls
   ```

2. Geh in den Ordner `setup`. Tippe `cd se` und drück Tab, das Terminal ergänzt den Namen:

   ```sh
   cd setup
   ls
   ```

3. Zeig auch die versteckten Dateien (Windows: `ls -Force`):

   ```sh
   ls -a
   ```

   Jetzt siehst du `.env`. Dort steht dein Schlüssel.

4. Frag Git, ob es `.env` kennt:

   ```sh
   git status
   git check-ignore -v .env
   ```

   `git status` erwähnt `.env` nicht. Der zweite Befehl zeigt, warum: `.gitignore:2:.env`. Zeile 2 der `.gitignore` hält die Datei aus Git heraus.

5. Geh eine Ebene hoch und prüfe, wo du bist:

   ```sh
   cd ..
   pwd
   ```

**Checkpoint:** `pwd` endet auf `compliance-search-ws2627`. Du hast `.env` mit `ls -a` gesehen, aber nicht in `git status`.

**Bonus:** Geh mit einem einzigen Befehl von `setup` nach `backend/tests` und wieder zurück in den Projektordner.

---

## Block 2: Programme starten mit uv (30 min)

### 2.1 Der Setup-Check

```sh
cd setup
uv run --env-file .env check.py
```

Du siehst fünf Zeilen, die mit `ok` beginnen.

| Du siehst | Lösung |
|---|---|
| `GATEWAY_KEY is missing` | `--env-file .env` vergessen, oder in `.env` steht noch `sk-...` |
| `uv: command not found` | Neues Terminal öffnen |
| `unexpected argument '--env-file'` | uv ist zu alt: `uv self update` |

### 2.2 Dasselbe ohne uv

```sh
python3 chat.py --model mock "hello"
```

Windows: `python` statt `python3`.

Das scheitert mit `ModuleNotFoundError: No module named 'openai'`. Das Python deines Systems kennt die Pakete des Projekts nicht. Jetzt mit uv:

```sh
uv run --env-file .env chat.py --model mock "hello"
```

uv hat die Pakete in den Ordner `.venv` gelegt und den Schlüssel aus `.env` mitgegeben. Deshalb starten wir im Projekt alles mit `uv run`.

### 2.3 Die Tests des Backends

```sh
cd ../backend
uv run pytest
```

Am Ende steht `8 passed`. Beim ersten Mal baut uv vorher die `.venv` für das Backend.

### 2.4 Den Server starten und fragen

1. Starte den Server:

   ```sh
   uv run uvicorn compliance_search.api.app:app --port 8000
   ```

   Er läuft, sobald `Uvicorn running on http://127.0.0.1:8000` dasteht. Das Terminal ist jetzt belegt.

2. Öffne im Browser `http://localhost:8000/docs`. Klick auf **POST /ask → Try it out**, trag eine Frage ein und klick **Execute**.

   Oder aus einem zweiten Terminal (Plus-Symbol im Terminal-Bereich), macOS und Linux:

   ```sh
   curl -X POST http://localhost:8000/ask -H 'content-type: application/json' -d '{"question": "How often must TLPT run?"}'
   ```

3. Schau ins erste Terminal: Dort steht deine Anfrage als `"POST /ask HTTP/1.1" 200 OK`.
4. Stopp den Server mit **Ctrl + C**.

### 2.5 Ein Paket hinzufügen und wieder verwerfen

1. Füg im Ordner `setup` ein Paket hinzu:

   ```sh
   cd ../setup
   uv add rich
   git status
   ```

   Git meldet zwei geänderte Dateien: `pyproject.toml` und `uv.lock`.

2. Öffne in VS Code links **Source Control** (das Symbol mit den Verzweigungen) und klick auf `pyproject.toml`. Grün ist die neue Zeile `"rich>=…"`.
3. Wir wollen das Paket nicht behalten. Klick bei beiden Dateien auf den Pfeil zurück (**Discard Changes**) und bestätige.
4. Bring die `.venv` wieder auf den Stand von `uv.lock`:

   ```sh
   uv sync
   git status
   ```

**Checkpoint:** Fünfmal `ok`, `8 passed`, eine JSON-Antwort von `/ask`, und `git status` meldet wieder, dass nichts zu committen ist.

**Merksatz:** Nach `uv add` gehören immer beide Dateien in denselben Commit, `pyproject.toml` und `uv.lock`.

**Bonus:** Schick über `/docs` eine leere Frage (`""`). Welchen Statuscode bekommst du, und wo im Ordner `backend/tests` wird genau das geprüft?

---

## Block 3: Git lokal (30 min)

Die Übungsdatei ist [`docs/tutorials/workshop-spielwiese.md`](workshop-spielwiese.md). Dort gibt es einen Abschnitt mit deinem Namen.

1. Geh in den Projektordner und stell sicher, dass du auf einem aktuellen `main` startest:

   ```sh
   cd ..
   git switch main
   git pull
   ```

2. Leg deinen Branch an:

   ```sh
   git switch -c DEL-44-workshop-<vorname>
   ```

   Unten links in VS Code steht jetzt dein Branch.

3. Öffne `docs/tutorials/workshop-spielwiese.md` und füll die **erste** Zeile unter deinem Namen aus. Speichern.
4. Öffne **Source Control**. Die Datei steht unter **Changes** mit einem `M` für geändert. Klick darauf: links der alte Stand, rechts der neue.
5. Klick auf das **Plus** neben der Datei. Sie wandert nach **Staged Changes**.
6. Schreib oben eine Nachricht, die sagt, was sich ändert, zum Beispiel `Fill in my operating system`, und klick **Commit**.
7. Jetzt dasselbe im Terminal. Füll die **zweite** Zeile aus, speichere, dann:

   ```sh
   git status
   git add docs/tutorials/workshop-spielwiese.md
   git commit -m "Add what I look forward to"
   ```

8. Schau dir deinen Verlauf an:

   ```sh
   git log --oneline -3
   ```

**Checkpoint:** Oben in der Liste stehen deine zwei Commits, darunter einer, der nicht von dir ist. `git status` meldet nichts zu committen.

| Du siehst | Lösung |
|---|---|
| Unten links steht `main` | Du hast auf `main` gearbeitet. Noch nicht committet: einfach Schritt 2 nachholen, die Änderung kommt mit. Schon committet: Hand heben, das ist Block 6 |
| `nothing to commit` beim Commit | Datei nicht gespeichert oder nicht gestaged |

**Bonus:** Rechtsklick auf die Datei im Explorer, dann **Open Timeline**. Dort stehen alle Commits dieser Datei.

---

## Block 4: Push, Pull Request, Review, Merge (35 min)

### 4.1 Hochladen

Klick in **Source Control** auf **Publish Branch**. Im Terminal wäre das:

```sh
git push -u origin DEL-44-workshop-<vorname>
```

Ein einfaches `git push` scheitert beim ersten Mal, weil GitHub den Branch noch nicht kennt. Ab dem zweiten Mal reicht `git push` oder der **Sync**-Knopf.

### 4.2 Pull Request öffnen

1. Öffne das Repo auf GitHub. Oben erscheint ein gelber Hinweis mit **Compare & pull request**. Klick darauf.
2. Titel: `DEL-44: Workshop-Abschnitt <Vorname>`.
3. Die Beschreibung ist mit unserer Vorlage vorausgefüllt. Ergänze den Jira-Link, schreib je einen Satz zu „What changes“ und „How I tested it“, und hake die Checkliste ab.
4. Rechts bei **Reviewers** wählst du dein Paar.
5. **Create pull request**.

### 4.3 Review (jetzt bist du die prüfende Person)

1. Öffne den Pull Request deines Paars und dort den Reiter **Files changed**.
2. Fahr mit der Maus über eine geänderte Zeile, klick auf das blaue **Plus** und schreib einen Änderungswunsch, zum Beispiel „Bitte ausschreiben statt abkürzen“. **Start a review**.
3. Oben rechts **Review changes → Request changes → Submit review**.

### 4.4 Änderungswunsch umsetzen (wieder als Autorin oder Autor)

1. Ändere die Zeile in VS Code, speichere, stage, committe.
2. **Sync** oder `git push`.
3. Lade den Pull Request im Browser neu: Der neue Commit steht im selben Pull Request.

### 4.5 Freigeben und mergen

1. Prüfende Person: **Files changed → Review changes → Approve → Submit review**.
2. Autorin oder Autor: **Merge pull request → Confirm merge**, danach **Delete branch**.
3. Beide holen den neuen Stand:

   ```sh
   git switch main
   git pull
   ```

**Checkpoint:** In deinem lokalen `main` stehen in der Übungsdatei dein Abschnitt **und** der deines Paars.

| Du siehst | Lösung |
|---|---|
| Kein gelber Hinweis auf GitHub | Reiter **Pull requests → New pull request**, bei `compare` deinen Branch wählen |
| Beim Push fragt VS Code nach einer Anmeldung | Im Browser bei GitHub anmelden und den Zugriff erlauben |
| **Merge** ist grau | Die Freigabe fehlt noch. Dein Paar muss **Approve** wählen |
| Du kannst deinen eigenen Pull Request nicht freigeben | Richtig so. Das macht immer eine zweite Person |

**Bonus:** Lösch den gemergten Branch auch lokal: `git branch -d DEL-44-workshop-<vorname>`.

---

## Block 5: Ein Konflikt, mit Absicht (25 min)

Ihr ändert beide dieselbe Zeile. Legt fest, wer **A** ist und wer **B**.

1. Beide, von einem aktuellen `main` aus:

   ```sh
   git switch main
   git pull
   git switch -c DEL-44-konflikt-<vorname>
   ```

2. Beide ändern in Teil 2 der Übungsdatei die Zeile eures Paars. Sprecht euch **nicht** ab, jede Person trägt einen anderen Lieblingsbefehl ein. Dann committen, **Publish Branch**, Pull Request öffnen.
3. **A** bekommt die Freigabe von B und mergt.
4. **B** lädt den eigenen Pull Request neu. GitHub meldet: **This branch has conflicts that must be resolved.**
5. **B** holt `main` in den eigenen Branch:

   ```sh
   git pull origin main
   ```

   Git meldet einen Merge-Konflikt in der Übungsdatei.

6. **B** öffnet die Datei in VS Code. Die Stelle ist markiert:

   ```text
   <<<<<<< HEAD
   Paar 1 (…): Unser Lieblingsbefehl ist uv run
   =======
   Paar 1 (…): Unser Lieblingsbefehl ist git status
   >>>>>>> …
   ```

   Oben steht deine Fassung, unten die aus `main`. Einigt euch jetzt zu zweit auf eine Zeile. Über der Stelle bietet VS Code **Accept Current Change**, **Accept Incoming Change** und **Accept Both Changes** an. Oder ihr schreibt die Zeile von Hand und löscht die drei Markierungszeilen.

7. **B** speichert, staged die Datei mit dem Plus, committet und klickt **Sync**.
8. **A** gibt den Pull Request von B frei, **B** mergt. Beide: `git switch main`, dann `git pull`.

**Checkpoint:** In `main` steht eure gemeinsame Zeile, und in der Datei gibt es keine Zeile mehr mit `<<<<<<<`, `=======` oder `>>>>>>>`.

| Du siehst | Lösung |
|---|---|
| `Need to specify how to reconcile divergent branches` | Schritt 5 aus Block 0 fehlt: `git config --global pull.rebase false`, dann noch einmal `git pull origin main` |
| Die Markierungen sind mit committet | Zeilen löschen, speichern, neuer Commit, Sync |

**Bonus:** Rollen tauschen und das Ganze mit einer neuen Zeile wiederholen.

---

## Block 6: Fehler rückgängig machen (10 min)

Ihr arbeitet auf einem neuen Branch, damit nichts davon in `main` landet:

```sh
git switch main
git pull
git switch -c DEL-44-rueckgaengig-<vorname>
```

### 6.1 Änderung verwerfen

1. Schreib irgendetwas in die Übungsdatei und speichere.
2. **Source Control → Pfeil zurück (Discard Changes)** neben der Datei.

Die Änderung ist weg. Sie kommt nicht wieder.

### 6.2 Letzten Commit zurücknehmen

1. Ändere die Datei noch einmal, speichere, stage, committe mit der Nachricht `Wrong commit`.
2. **Source Control → … → Commit → Undo Last Commit**.

Der Commit ist weg, deine Änderung liegt wieder unter **Staged Changes**. Hol sie mit dem **Minus** dort heraus und verwirf sie wie in 6.1.

**Checkpoint:** `git status` meldet nichts zu committen, und `git log --oneline -1` zeigt nicht `Wrong commit`.

Danach zeigt Elias zwei Fälle am Beamer: versehentlich auf `main` committet, und einen gemergten Pull Request mit **Revert** zurücknehmen.

---

## Block 7: Dein echtes Ticket (5 min)

1. Such dir in Jira dein nächstes Ticket.
2. Leg den Branch dafür an:

   ```sh
   git switch main
   git pull
   git switch -c DEL-<nummer>-<kurzes-thema>
   ```

**Checkpoint:** Unten links in VS Code steht der Branch deines echten Tickets. Ab hier läuft alles wie in Block 3 bis 5.

Zum Nachschlagen: der [Spickzettel](../how-to/git-spickzettel.md) mit allen Befehlen und den häufigsten Fehlern.
