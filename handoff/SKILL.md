---
name: handoff
description: Write or update a handoff document so the next agent with fresh context can continue this work.
---

# Handoff

## Overview

Write or update a branch-scoped handoff document so a fresh agent can continue the current work without mixing context from other branches or stale requirements.

The handoff file is always:

```text
<parent-of-project-root>/.handoff/<project-name>/<context-name>/HANDOFF.md
```

## Workflow

1. Identify the project root.
   - In a Git repo, use `git rev-parse --show-toplevel`.
   - In an ADE view, follow ADE rules and use the active view/project root instead of assuming Git.
   - If no SCM root is detectable, use the current working directory and state that assumption.
2. Identify the branch or work context.
   - In Git, use `git branch --show-current`.
   - If detached, use a short commit/ref description.
   - In ADE, use the active view or transaction identity.
   - If no context is detectable, use `unknown-context`.
3. Identify and sanitize the project name.
   - Use the project root directory name by default.
   - Replace `/`, whitespace, and shell-sensitive punctuation with `-`.
   - Keep letters, numbers, `.`, `_`, and `-`.
   - Avoid empty names; fall back to `project`.
4. Sanitize the context name for a directory.
   - Replace `/`, whitespace, and shell-sensitive punctuation with `-`.
   - Keep letters, numbers, `.`, `_`, and `-`.
   - Avoid empty names; fall back to `unknown-context`.
5. Put the handoff one directory above the project root.
   - Use `<parent-of-project-root>/.handoff/<project-name>/<context-name>/HANDOFF.md`.
   - Do not write the handoff folder inside the Git worktree.
   - If the parent directory is not writable, stop and tell the user the intended path and the write failure.
6. Check for the existing handoff at that path.
   - If it exists, read it before updating.
   - Preserve still-relevant facts, decisions, commands, blockers, and file paths.
   - Replace or remove stale context when requirements changed.
   - Record important removed or superseded context under `Changed or Removed Context`.
7. Create or update the handoff using the required structure below.
8. Final response must include the absolute path to the handoff file and tell the user they can start a fresh conversation with that path.

## Required Document Structure

Use exactly these top-level sections:

```markdown
# Handoff: <branch-or-context-name>

## Goal

## Current Progress

## What Worked

## What Didn't Work

## Changed or Removed Context

## Next Steps
```

## Content Rules

- Keep the handoff practical and specific enough for a fresh agent.
- Include concrete file paths, commands run, command results, branch names, tickets, requirements, and known blockers.
- Make `Next Steps` ordered and action-oriented.
- Do not append old history forever. When requirements changed, replace stale sections and summarize what was removed or superseded.
- Do not mix contexts from other branches. If the current branch/context changes, write to that context's own handoff path.
- Use the hidden `.handoff/` directory one level above the project root, so normal `ls` inside the project does not show the handoff files.
- Keep handoffs outside the Git worktree so they do not appear in `git status` and do not require `.gitignore` changes.
- Respect user read-only instructions. If the user asks for investigation only, draft the handoff content in the response instead of writing the file.

## Final Response

After writing or updating the handoff, respond with:

- The absolute path to `<parent-of-project-root>/.handoff/<project-name>/<context-name>/HANDOFF.md`.
- A brief note that the user can start a fresh conversation with just that path.
- Any assumptions made about project root, project name, context name, or parent-directory writability.
