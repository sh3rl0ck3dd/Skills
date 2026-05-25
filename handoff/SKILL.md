---
name: handoff
description: Write or update a handoff document so the next agent with fresh context can continue this work.
---

# Handoff

## Overview

Write or update a branch-scoped handoff document so a fresh agent can continue the current work without mixing context from other branches or stale requirements.

The handoff file is always:

```text
<project-root>/.handoff/<context-name>/HANDOFF.md
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
3. Sanitize the context name for a directory.
   - Replace `/`, whitespace, and shell-sensitive punctuation with `-`.
   - Keep letters, numbers, `.`, `_`, and `-`.
   - Avoid empty names; fall back to `unknown-context`.
4. Keep the handoff hidden from Git when possible.
   - In a Git repo, check whether `.handoff/` is already ignored with `git check-ignore .handoff/`.
   - If it is not ignored and the user did not request read-only behavior, add `.handoff/` to the project root `.gitignore` using the normal repo editing rules.
   - If `.gitignore` cannot be safely changed, still write the handoff under `.handoff/` and tell the user that Git ignore setup was not completed.
5. Check for the existing handoff at `.handoff/<context-name>/HANDOFF.md`.
   - If it exists, read it before updating.
   - Preserve still-relevant facts, decisions, commands, blockers, and file paths.
   - Replace or remove stale context when requirements changed.
   - Record important removed or superseded context under `Changed or Removed Context`.
6. Create or update the handoff using the required structure below.
7. Final response must include the absolute path to the handoff file and tell the user they can start a fresh conversation with that path.

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
- Use the hidden `.handoff/` directory so normal `ls` does not show the handoff files.
- In Git repos, keep `.handoff/` ignored so handoff files do not appear in `git status`.
- Respect user read-only instructions. If the user asks for investigation only, draft the handoff content in the response instead of writing the file.

## Final Response

After writing or updating the handoff, respond with:

- The absolute path to `.handoff/<context-name>/HANDOFF.md`.
- A brief note that the user can start a fresh conversation with just that path.
- Any assumptions made about project root, context name, or Git ignore setup.
