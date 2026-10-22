# 0001: We record decisions in this folder

- Status: Accepted
- Date: 2026-10-23
- Owner: Deloitte AI & Data team

## Context

The team makes many technology choices over the semester. Without a record, the reasons get lost and choices get reopened.
The task asks for a short decision record per technology choice.

## Decision

Each decision gets a numbered Markdown file in `docs/decisions/`, based on [`0000-template.md`](0000-template.md), merged through a reviewed pull request.

## Alternatives

| Option | Why not |
|---|---|
| A section in the README | Grows without limit and mixes with setup instructions |
| A wiki or a shared document | Lives outside the repo and outside review |

## Consequences

Records are cheap to write and easy to find. Old records stay as they were, so the history of a decision stays readable.
