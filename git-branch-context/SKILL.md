---
name: git-branch-context
description: compare the current checked-out git branch against master, summarize what changed, infer the branch purpose, and preserve a compact branch context snapshot for follow-up questions, edits, and alignment decisions. use when working in a git repo and the user asks what is different from master, what the branch is for, what changed, or how to keep later changes aligned with earlier branch work.
---

# Git Branch Context

## Overview

Use this skill to inspect the currently checked-out branch in a local git repository, compare it to `master`, and turn the diff into a reusable context snapshot. Use that snapshot as a working reference for later questions so new edits, explanations, and recommendations can stay aligned with the branch's existing direction when appropriate.

## Core workflow

1. Confirm the repository is a git checkout and identify the active branch.
2. Compare the current branch against `master` using the merge-base-aware diff (`master...HEAD`) unless the user explicitly asks for another comparison.
3. Summarize the change set in plain language:
   - what files changed
   - what the code or content is doing now
   - what the branch appears to be for
   - any visible patterns, dependencies, or risks
4. Build a compact branch context snapshot and treat it as the source of truth for follow-up questions in the same conversation.
5. When asked to change something, check whether the change fits the existing branch direction, reuses the same patterns where relevant, and avoids undoing prior work unless the user explicitly wants a broader rewrite.

## Branch context snapshot

Always preserve a short, reusable snapshot with these fields when available:

- `branch_name`
- `base_branch` (usually `master`)
- `branch_purpose`
- `summary_of_changes`
- `key_files`
- `design_patterns_or_conventions`
- `behavioral_invariants`
- `open_questions_or_risks`

Treat this snapshot as a lightweight working memory of the branch’s current direction, not as a rigid source of truth.
Update or discard parts of the snapshot when newer changes make earlier assumptions outdated. Reuse it when answering follow-up questions, suggesting edits, or reviewing new changes.

## What to report

Start with a brief intro that answers: “what is this branch for?” Then provide a concise diff summary. Prefer short, useful language over exhaustive file-by-file narration.

Use this structure by default:

### Branch intro
One or two sentences describing the likely purpose of the branch.

### What changed from master
A compact summary of the major changes and the files or areas affected.

### Branch context snapshot
A short bullet list or compact block with the reusable context fields above.

### Alignment guidance
State how future changes should stay aligned with the branch’s existing work. Call out the conventions, patterns, and constraints that should be preserved.

## Follow-up behavior

When the user asks a later question about the branch, answer using the saved branch context first. Then only extend or refine that context if the new request introduces genuinely new information.

When the user asks to modify something, check the change against the stored branch context and answer using this rule:

- **Aligned**: the change reasonably fits the current branch direction or cleanly extends it.
- **Independent**: the change is mostly unrelated to earlier work and does not need strict alignment.
- **Needs adjustment**: the change unintentionally conflicts with important existing behavior, conventions, or assumptions.

When a change needs adjustment, explain the mismatch and suggest the smallest change that keeps the work consistent with the branch.

## Practical git signals to inspect

Use these signals to infer branch purpose and summarize changes:

- commit subjects on `master..HEAD`
- changed file names and directories
- repeated terminology in code, tests, docs, or config
- new APIs, data shapes, feature flags, or migrations
- renamed or removed files that suggest a refactor or cleanup

## If a repo is available

If local repository access is available, run the helper script at `scripts/git_branch_context.py` to collect the branch report. If not, ask the user to provide the relevant git output or repository context.

## Resources

- `scripts/git_branch_context.py`: collects branch metadata, diff summary, and a reusable context snapshot.
