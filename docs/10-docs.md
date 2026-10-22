# How you document

Your docs live in `docs/`, in five folders. Each folder answers one kind of question.
Put a page where its reader looks for it, not where you happened to write it.

The structure follows [Diátaxis](https://diataxis.fr/). You do not need to read about it: the folders do the sorting.

## The five folders

| Folder | The reader wants to | Example page |
|---|---|---|
| [`tutorials/`](tutorials/) | Learn by doing, from zero | From a fresh clone to the first answer with a citation |
| [`how-to/`](how-to/) | Get one task done | Run the sync locally. Re-index one document. Add a test question. |
| [`reference/`](reference/) | Look up a fact | `POST /ask`, database schema, chunk metadata, environment variables |
| [`explanation/`](explanation/) | Understand why | The architecture. Why we chunk by article. How currency works. |
| [`decisions/`](decisions/) | Know what was decided, and why | `0003-vector-store-supabase.md` |

Not sure where a page goes? Ask what the reader is doing when they open it.
Learning: tutorial. Working: how-to. Checking a detail: reference. Thinking: explanation.

## Three rules

1. **The README is an entry point.** What the app is, a quickstart of three lines, links into `docs/`. Nothing longer.
2. **A pull request that changes behaviour updates the docs.** The pull request template asks for it. Reviewers check it.
3. **Decision records are never edited.** A new decision supersedes an old one. See [`decisions/`](decisions/README.md).

## What not to do

- One page per person or per sprint. Pages belong to topics, not to authors.
- A how-to that explains the architecture, or an explanation full of commands. Split it and link.
- Docs in a wiki, a Google Doc or a chat. If it is not in the repo, it does not exist.
