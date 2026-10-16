# Contributing Agreement

This document defines the workflow for our team on the Bike Demand project. Every team member must follow these rules when making changes to the repository.

## 1. Branch and Commit Naming

- **Branches:** All work must be done on a dedicated branch created from `main`. Direct commits to `main` are not allowed.
  - Naming convention: `lab-<number>-<short-topic>`
  - Example: `lab-01-workflow`
- **Commits:** Commit messages must be short, clear, and written in the imperative mood to describe the exact change.
  - Example: `Normalize team labels`
- **Staging rules:** Always inspect changes using `git status --short` and `git diff` before staging. Only stage intended source, test, or documentation files. Never commit secrets, credentials, virtual environments, or generated artifacts.

## 2. Local Checks

Before pushing a branch or opening a Pull Request, the author must run all local checks from the project root using the locked environment and verify that they pass:

1. **Synchronize environment and run preflight:**
   - `uv sync --locked`
   - `uv run --locked python -m bike_demand.preflight`

2. **Run code quality and formatting checks (Ruff):**
   - `uv run --locked ruff check`
   - `uv run --locked ruff format --check`

3. **Run automated test suites (Pytest):**
   - `uv run --locked pytest -q -m infra`
   - `uv run --locked pytest -q -m lab1`
   - `uv run --locked pytest -q`

Do not skip tests, modify existing assertions, or disable linter checks to hide a failure.

## 3. Pull Requests and Peer Review

- **Pull Request description:** Every Pull Request must stay small and focused on a single task. The description must state:
  - What changed in the code, tests, or documentation.
  - How the change was checked locally and the actual command outcomes.
  - Any unresolved blockers (such as blocked remote CI runs).
- **Peer review:**
  - At least one other team member must review the Pull Request by inspecting the code and test diff together.
  - The reviewer must verify that the behaviour contract is respected, leave feedback, and formally approve the Pull Request.
  - **No self-approval:** Contributors are strictly forbidden from approving their own Pull Requests.

## 4. Who Merges and When

- **When to merge:** A Pull Request can be merged into `main` only when all of the following conditions are met:
  1. All local `ruff` and `pytest` checks pass on the latest commit of the branch.
  2. Remote GitHub Actions checks pass on the latest commit (or any remote CI blocker is explicitly recorded in the PR).
  3. All review comments have received a response and a teammate has approved the Pull Request.
- **Who merges:** Once a teammate has approved the Pull Request and all checks are confirmed on the current revision, the Pull Request author (or the approving reviewer) merges the Pull Request into `main`.
