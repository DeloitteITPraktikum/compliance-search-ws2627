# 0006: Document sync via GitHub Actions cron and python script 

- Status: Proposed 
- Date: 2026-11-09
- Owner: LeonardSchachtel

## Context

The documents of the Documents API must be synchronized regularly. They should be synchronized automaticly every day, but there should also be an option to start the syncronization manually. In phase 1, the documents live as a folder in the Git repo; in phase 2, they move to the database. The sync is performed by a python script that has to be executed on a schedule. At first the synchronization of the documents has to work without a backend, later the backend has to be woken up to sync the documents in the database with those of Documents API.

## Decision

We use a GitHub Actions workflow with a schedule (cron) trigger as the scheduler, plus workflow_dispatch for manual runs.

Phase 1: The workflow runs the python script directly against the document folder in the repo.
Phase 2: The workflow runs the python script against the contents of the database. 

Depending on how quickly the backend and the database is ready for use, the python script will be transferred to the backend in phase 1 or phase 2 and the GitHub workflow aswell as the python script will be adjusted.

## Alternatives

| Option | Why not |
|---|---|
| Cron job in the backend that starts the Python script | The free backend sleeps after 15 minutes of inactivity and cannot trigger the job reliably. |
| External cron service that regularly pings the backend | Adds a dependency and another service to configure and monitor. Sync failures would be harder to see than in the Actions logs. |
| Manual sync | Error-prone and dependent on individual people. Data would not be reliably up to date. |
| Sync on every push | Does not cover later changes in the database, since those do not trigger a push to the repo. |

## Consequences

- The documents do not have to be synced by every team member individualy, because they can just git pull the main branch an they will recieve all documents available.
- The documents are synced automaticly, so no team member has to check the Documents API for change of documents regulary.
- The switch from running the python script in GitHub to running it on the backend, will definitely require a change of the GitHub workflow and possibly also some parts of the python script.
- We have to keep in mind while changing the GitHub workflow that our backend goes into sleep mode after 15min of inactivity. 