# 0003: Name branches after their Jira ticket

- Status: Proposed
- Date: 2026-11-06
- Owner: Team

## Context

We track our work in the Jira project DEL. Without a shared naming scheme, branch names do not show which ticket they belong to, and it is hard to tell what a branch is for.
Jira will not get the GitHub for Atlassian integration: the Jira admin decided against it. So Jira cannot link branches and pull requests on its own, and the branch name is our link between the two.
The team agreed on a common convention. It is a guideline, not a strict rule: a branch without a fitting ticket, such as a small fix, may use a short descriptive name instead.

## Decision

Each branch is named after one Jira ticket: the ticket key, then a short topic in lowercase with hyphens, for example `DEL-3-folder-structure`. Commit messages do not need the ticket key, because the branch name already carries it.

## Alternatives

| Option | Why not |
|---|---|
| None | The team adopted the convention directly, without comparing other schemes |

## Consequences

Every branch points to its ticket, so reviewers find the context of a change quickly. Without the integration, the link only goes one way: from GitHub you find the ticket by its key, but Jira does not show the branch or pull request.
Work needs a ticket before the branch, and one branch covers one ticket. Nothing enforces the format, so we watch for drift in reviews.
