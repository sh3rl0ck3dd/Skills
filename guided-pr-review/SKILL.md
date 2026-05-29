---
name: guided-pr-review
description: "guide codex through interactive pull request walkthroughs. use when the user wants to understand or review a pr step by step, identify the best entry point, inspect the first file and line to read, explain changed code line by line or function by function, pause for questions at each stop, compare files in review order, or learn what a pull request is doing before leaving review comments."
---

# Guided PR Review

## Purpose

Run a conversational PR walkthrough. Teach the user what the PR does by choosing a sensible entry point, walking changed files in dependency/runtime order, explaining changed lines and functions, asking review questions, and pausing for the user before advancing.

This is an explainer and review workflow. Do not edit files, commit, push, or leave PR comments unless the user explicitly asks.

## First response in a walkthrough

1. Establish the source of the PR:
   - If the PR branch is already checked out, use the local git diff.
   - If the user gives a PR number or URL and `gh` is available, inspect it with `gh pr view` and `gh pr diff`; do not switch branches without explicit permission.
   - If no base is given, try `origin/main`, `origin/master`, `main`, then `master`.
2. Build a diff map before teaching:
   - Prefer the bundled helper: run `scripts/pr_diff_index.py --base <base-ref>` from this skill directory when possible.
   - Otherwise run `git diff --name-status --find-renames <merge-base>...HEAD`, `git diff --stat <merge-base>...HEAD`, and file-specific diffs.
3. Reply with:
   - A one-paragraph PR story in plain English.
   - The proposed review order as a numbered list of files.
   - The first stop in `file:line` format.
   - A short reason this is the entry point.
   - A pause prompt: “Ask anything here, or say `next` to continue.”

Do not start dumping every file at once. The skill is interactive.

## Entry point selection

Choose the first file by following the code path a real request, job, command, render, import, or public API call would hit first. Do not rely on alphabetical order or diff order.

Ranking rules:

1. Start at the changed runtime boundary when present: route, controller, handler, CLI command, job scheduler, page, component entry, public exported API, plugin hook, middleware, migration entry, config key, or event consumer.
2. Then move inward: orchestrator/service/use-case, domain logic, repository/data access, models/types/schema, utilities/helpers.
3. Put tests after the production path unless the PR is primarily a bug fix whose added/changed test best explains the desired behavior. In that case, start with the test as the story, then jump to the production fix.
4. Put docs, generated files, formatting-only files, snapshots, and lockfiles last unless they are the core change.
5. For refactors, start at the public symbol or caller whose behavior should remain stable, then inspect moved/renamed internals.
6. For deletions, start at the caller/import/config that stops using the deleted code, then explain the deleted file.
7. For cross-cutting changes, start with the smallest boundary that fans out to the rest of the PR.

Choose the first line within the first file as the earliest changed executable or declarative line that makes the new behavior happen. Use the function/class/module declaration for new files, the changed branch/assignment/call for modified files, the changed key for config, and the caller-side removal for deletions.

## Review order planning

Create and maintain an internal walkthrough queue:

- Files: ordered by entry point and dependency flow.
- Within each file: changed functions/classes/sections in execution order.
- Within each function: changed line groups in logical order.
- For each stop: include the exact `file:line` anchor, surrounding symbol, and whether it is an added, modified, deleted, or context line.

When the diff is large, say that the walkthrough will focus on significant changed lines by default. Group trivial imports, braces, formatting, and repeated boilerplate unless the user asks for literal every-line mode.

## Checkpoint format

At every line/function stop, use this compact structure:

```markdown
### Stop N — `path/to/file.ext:123` in `function_or_section`

**What you are looking at:** [plain-English description]
**What changed:** [specific change]
**Why it matters:** [how this contributes to the PR]
**Reviewer lens:** [one risk, invariant, edge case, or reason it looks safe]
**Question for you:** [one useful comprehension or review question]

Ask anything about this stop, or say `next`.
```

Keep each stop short. Use deeper explanations only when the user asks.

## Conversation controls

Understand these user commands during the walkthrough:

- `next`: move to the next changed line group; if none remains, move to the next function; if none remains, summarize the file and move to the next file.
- `next line`: advance to the next changed line group in the current function.
- `next function`: skip the rest of the current function and move to the next changed function/section in the same file.
- `next file`: summarize the current file and move to the next file.
- `back`: return to the previous stop.
- `deeper`, `why`, or `explain more`: expand the current stop with nearby code, data flow, and assumptions.
- `show callers`: inspect callers/usages with `rg`, imports, references, or language-aware tooling if available.
- `show tests`: jump to tests that cover the current behavior.
- `risk check`: focus on bugs, edge cases, regressions, security, performance, and missing tests for the current stop.
- `summary`: summarize progress so far and list remaining files.
- `skip`: skip the current trivial line group.
- `done`: end the walkthrough with a PR-level summary and review recommendations.

If the user asks a free-form question, answer it using the current stop and surrounding code, then stay at the same stop until the user advances.

## Teaching style

Explain code as a senior reviewer teaching a teammate:

- Translate syntax into intent.
- Connect each line to the PR’s larger behavior.
- State assumptions and uncertainty plainly.
- Prefer “this line means...” over abstract language.
- Ask one helpful question at each stop. Alternate between comprehension questions and reviewer questions.
- Do not quiz aggressively; if the user answers incorrectly, correct gently and continue.

Good questions include:

- “What input would cause this branch to run?”
- “What could be null, empty, or unauthorized here?”
- “Where would you expect this behavior to be tested?”
- “Does this change preserve the old behavior for existing callers?”
- “What happens if this dependency fails or returns no result?”

## Review judgment

This workflow teaches first and reviews second. Still surface concrete review concerns when found:

- correctness regressions
- missing or weak tests
- unhandled edge cases
- security or authorization gaps
- data migration or compatibility risks
- performance changes in hot paths
- confusing naming or maintainability issues

Do not invent issues. When a concern is speculative, label it as a question to verify.

## File completion

When finishing a file, summarize before moving on:

```markdown
## Finished `path/to/file.ext`

**Role in the PR:** [one sentence]
**Key lines:** `line`, `line-range`, `line`
**What you should remember:** [2-3 bullets max]
**Possible review notes:** [only concrete concerns, or “none so far”]

Next file: `path/to/next.ext:line` — [why this comes next]
```

Then pause for the user.

## Final PR summary

When all files are done or the user says `done`, end with:

- The PR story in 3-6 bullets.
- The final review order with key line anchors.
- The main behaviors changed.
- The tests or validation observed, plus missing coverage if any.
- Concrete review comments to consider, phrased politely and only when justified.
- Open questions for the PR author.

## Useful commands

Use these as needed from the repository root:

```bash
git status --short
git branch --show-current
git merge-base HEAD origin/main
git diff --name-status --find-renames <merge-base>...HEAD
git diff --stat <merge-base>...HEAD
git diff --unified=80 <merge-base>...HEAD -- path/to/file
nl -ba path/to/file | sed -n 'START,ENDp'
rg -n "symbol_or_call" .
```

If `origin/main` is wrong, retry with the base branch indicated by the PR metadata or user.
