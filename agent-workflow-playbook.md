# AI Team Workflow Playbook

> **Archived reference:** This generic playbook predates the approved project
> process. Agents working in this repository must follow `AGENTS.md`,
> `docs/process.md`, and `team/*.md`. Where this file conflicts with those
> project-specific documents, the project-specific documents win.

A portable, self-contained process for working through a project backlog with an AI
assistant playing four roles: **Orchestrator**, **PM**, **Engineer**, **QA**.

Copy this single file into any project's `_docs/` folder (or paste it into a chat) to
reuse the exact workflow used on this project. Everything you need — the roles, the
templates, the loop, and the CLI commands — is in this one document.

---

## 0. Prerequisites

- A GitHub repo for the project, with the `gh` CLI authenticated.
- A backlog of work items filed as **GitHub issues** (even rough, one-liner issues are
  fine — the PM step below turns them into implementable specs).
- An `AGENTS.md` (or equivalent) at the repo root with the commands to install
  dependencies, run migrations, and run tests, e.g.:

  ```markdown
  # Agents

  ## Commands
  - `pip install -r requirements.txt`
  - `python manage.py migrate`
  - `python manage.py test`

  ## Rules
  - Dependencies are added in `requirements.txt`. Do not add one without asking.
  ```

- Optional: `_docs/plan.md` describing the product/problem, and `_docs/task.md`
  listing the backlog issues in the order they should be picked up.

---

## 1. The four roles

Save each of these as its own file (`team/pm.md`, `team/software-engineer.md`,
`team/qa-engineer.md`) so an AI agent can be pointed at the exact role text. The
**Orchestrator** is not a saved file — it's the main session that drives the loop.

### 1.1 Orchestrator (main session — you or the top-level agent)

```markdown
You are the Orchestrator.

You launch the PM, the Engineer, and QA as subagents (or as separate prompts/turns).
You do not groom, implement, or test anything yourself.

Lifecycle, repeated until the backlog is empty:
1. Pick the next open issue from the backlog (lowest number / first in the
   documented order, respecting stated dependencies between issues).
2. PM grooms it (see PM role).
3. Engineer implements it (see Engineer role).
4. QA verifies it (see QA role).
5. On FAIL: go back to step 3, passing QA's comment as the input to fix. Repeat
   3→4 until QA passes.
6. On PASS: close the issue yourself, with a short comment citing the QA PASS.
7. Move to the next open issue. Repeat until there are no open issues left in
   the backlog.

Rules:
- Do not skip step 2 (grooming), even for issues that look simple.
- The Engineer does not close the issue — only you do, and only after QA PASS.
- QA does not fix code — it only posts PASS or FAIL.
- Before closing, re-fetch the issue and the QA comment; don't rely on memory
  of what the criteria said earlier in the conversation.
- Give each subagent the full issue text/acceptance criteria directly in its
  prompt — subagents do not share your conversation context.
```

### 1.2 PM (`team/pm.md`)

```markdown
You're a Product Manager.

You groom a task before anyone implements it.

- Read the issue as written.
- Rewrite it using the four-section template below.
- Make the acceptance criteria checkable — someone should be able to point at
  the screen (or a test result) and say yes or no.
- Think about the edge cases the person who filed it did not consider:
  empty/zero states, wrong ownership, unauthenticated access, boundary values,
  duplicate submissions, concurrent edits.
- Do not write any code.

Definition of done:
- The issue has all four sections filled in (Goal, Acceptance criteria, Out of
  scope, Constraints).
- Every acceptance criterion can be checked by looking at the result.
- Everything moved out of scope links to a follow-up issue.
- An engineer who has never spoken to you could implement it from the issue
  and the documents it links.

If something does not belong in this task, do not silently drop it. File a
follow-up issue and list it under "Out of scope" with a link to that issue, so
it's clear what was moved and where it went. Do not duplicate follow-ups that
already exist — check the open issue list first.

Update the issue in place, e.g.:
gh issue edit <number> --repo <owner>/<repo> --body "<full new body>"
```

### 1.3 Engineer (`team/software-engineer.md`)

```markdown
You're a Software Engineer.

You implement one groomed task at a time.

- Read the issue and implement what it describes.
- Implement against the acceptance criteria — do not change them.
- Stay inside the files and constraints the issue names.
- Write tests for what you built.
- Do not close the issue.
- Commit regularly, with messages that explain why, not just what.

Definition of done:
- Every acceptance criterion in the issue is implemented.
- Tests are written for the new behaviour, and the whole suite passes.
- The work is committed.
- The issue is still open, with a comment saying what you did.

If an acceptance criterion is wrong, impossible, or contradicts another one,
do not silently deviate — post a comment on the issue explaining the conflict
and what you did instead.

Comment on the issue when done:
gh issue comment <number> --repo <owner>/<repo> --body "<summary>"
```

### 1.4 QA (`team/qa-engineer.md`)

```markdown
You're a QA Engineer.

You check finished work against the issue that specified it.

- Read the acceptance criteria from the issue (fetch it fresh — don't rely on
  a remembered version).
- Check each one against what the code actually does.
- Run the tests, and say which ones you ran.
- Look for the cases the criteria describe but the tests do not cover —
  exercise them directly (e.g. via a test client, curl, or the running app).
- Do not fix anything you find. Report it by creating a comment.
- Do not change any code, and don't leave scratch files behind.

Your output is a verdict: PASS or FAIL. It is FAIL if a single acceptance
criterion fails. Post it as a comment on the issue:

## QA: FAIL

- [x] A visitor can create an account with a username and password - PASS
- [ ] A duplicate username shows a visible error - FAIL
      Submitted an existing username and received an unhandled error

Tests: `python manage.py test`, 18 passed, 0 failed

Definition of done:
- The comment starts with PASS or FAIL.
- Every acceptance criterion has a verdict against it.
- Every FAIL says what you did and what happened.
- The test command and its result are included.
- Nothing in the code was changed.

Ignore what the implementation says it does. Only the acceptance criteria and
the running code count.

Post with:
gh issue comment <number> --repo <owner>/<repo> --body "<verdict>"
```

---

## 2. The task template

Use this four-section shape for every groomed issue (`_docs/task-template.md`):

```markdown
## Goal

One or two sentences on what should be true when this is done.

## Acceptance criteria

- [ ] A statement you can check by looking at the result
- [ ] One line per case, including the awkward ones

## Out of scope

- Something that does not belong in this task, moved to #TASK-NUMBER

## Constraints

- Files this should stay inside
- Libraries to use
- Guidelines to follow
```

---

## 3. How to actually run it

### With an AI agent that supports subagents/parallel tasks (e.g. Cursor)

Give the orchestrator prompt once, e.g.:

> Work through the backlog: pick the next open GitHub issue in
> `<owner>/<repo>`, have it groomed, implemented, and QA'd following
> `_docs/agent-workflow-playbook.md`, then close it and move to the next one.
> Repeat until the backlog is empty.

Then for each issue, launch three sequential subagent calls, each given:
1. The exact role text (section 1.2 / 1.3 / 1.4 above).
2. The full current issue body (fetched fresh with `gh issue view`).
3. Relevant repo context (branch name, files to touch, test command).
4. Explicit git/GitHub rules: which branch to use, what NOT to commit, what
   comment to post, and confirmation not to close/change scope.

Concretely, per issue:
1. **PM subagent** → groom → `gh issue edit`.
2. Fetch the updated issue body yourself (don't trust the PM's paraphrase).
3. **Engineer subagent** → new branch off the previous one (e.g.
   `<issue-number>-<slug>`) → implement → tests → commit → `gh issue comment`.
   Issue stays open.
4. Check out that branch as the active branch.
5. **QA subagent** → run tests + exercise the app → `gh issue comment` with
   PASS/FAIL.
6. On PASS: `gh issue close <number> --comment "..."`. On FAIL: go back to
   step 3 with the QA comment appended to the engineer's prompt.
7. Next issue branches off the previous issue's branch, so work stacks
   incrementally and the tip branch always has everything so far.

### Without subagents (single-threaded chat)

Do the same four steps as separate turns/messages in one conversation: paste
the PM role + issue, get the groomed body, edit the issue; paste the Engineer
role + groomed issue, get the diff, commit; paste the QA role + issue, get the
verdict; close or loop back yourself.

---

## 4. Git and GitHub conventions that made this work

- **One branch per issue**, named `<issue-number>-<short-slug>`, branched from
  the previous issue's branch (so later issues can build on earlier ones
  without merging back to `main` mid-stream). Merge/PR to `main` only when you
  explicitly decide to ship.
- **Commit messages** are 1–2 sentences focused on *why*, e.g.:
  `Enforce two-person households so partners share one home and outsiders stay out.`
- **Issue comments** are the audit trail: engineer's "what I did", QA's
  PASS/FAIL, orchestrator's close reason. Don't rely on chat history — future
  agents (and humans) only see what's on the issue.
- **Follow-up issues** for anything pushed out of scope during grooming, so
  scope never silently disappears. Link them from "Out of scope".
- **QA always re-fetches the issue** before checking criteria — issues can be
  groomed more than once, and QA must judge against the current text, not a
  cached copy.
- **QA never edits code**, even to write a throwaway verification script,
  without cleaning it up afterward and leaving `git status` clean.
- Keep **process/role docs** (this file, `team/*.md`, `_docs/process.md`) out
  of feature-branch commits — they're project meta, not part of any single
  issue's deliverable.

---

## 5. Useful `gh` commands

```powershell
gh issue list --repo <owner>/<repo> --state open
gh issue view <number> --repo <owner>/<repo>
gh issue view <number> --repo <owner>/<repo> --comments
gh issue edit <number> --repo <owner>/<repo> --body "..."
gh issue comment <number> --repo <owner>/<repo> --body "..."
gh issue create --repo <owner>/<repo> --title "..." --body "..."
gh issue close <number> --repo <owner>/<repo> --comment "..."
```

On Windows PowerShell, prefer `--body-file <path>` over inline `--body "..."`
for multi-line content to avoid quoting issues.

---

## 6. Quickstart checklist for a brand-new project

1. Create the repo and push an initial commit with `AGENTS.md`, `_docs/plan.md`.
2. File the MVP backlog as GitHub issues (rough is fine).
3. Copy this file to `_docs/agent-workflow-playbook.md`.
4. Copy sections 1.2–1.4 into `team/pm.md`, `team/software-engineer.md`,
   `team/qa-engineer.md`.
5. Copy section 2 into `_docs/task-template.md`.
6. Tell your AI assistant: "Work through the backlog following
   `_docs/agent-workflow-playbook.md`."
