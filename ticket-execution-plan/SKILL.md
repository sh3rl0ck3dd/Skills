---
name: ticket-execution-plan
description: Use after planning, requirement gathering, ticket analysis, issue triage, or branch intent review is complete and the user wants a full step-by-step implementation checklist. Produces bite-sized, tickable execution tasks with why each task is needed, which files are involved, what change to make, and the expected end result.
---

# Ticket Execution Plan

## Overview

Turn a known ticket scope into a concrete execution plan that can be followed and checked off one step at a time. The output should be detailed enough for implementation, review, and handoff, without grouping unrelated files into a single vague task.

Use this skill only when the requirements are already known or mostly known. If discovery is still incomplete, ask the smallest number of blocking questions first, then produce the plan.

## Planning Rules

- Start from the ticket goal, accepted requirements, current branch intent, constraints, and known risks.
- Keep each task reviewable and understandable. A good task usually changes one behavior, one layer, one test fixture, one API contract, or one UI state.
- Do not make tasks so small that they are busywork, such as "add one log line" or "rename one local variable", unless that is the whole meaningful change.
- Do not make tasks so large that the user cannot predict the diff, such as "update the frontend" or "fix auth flow" across dozens of files.
- Prefer tasks that can be implemented and verified independently.
- Order tasks by dependency: contracts and data shape first, implementation next, UI or callers after that, tests and cleanup last.
- Include verification close to the relevant task, not only at the end.
- If file names are not yet known, say how to locate them and mark the file list as tentative.

## Output Shape

Use this structure:

```markdown
**Execution Plan**

Assumptions:
- <assumption or "None">

Acceptance target:
- <what must be true when the plan is done>

- [ ] Step 1: <short action title>
  Why: <why this step is necessary>
  Files: <exact files or likely paths>
  Change: <specific implementation change>
  End result: <observable state after this step>
  Verify: <focused check, test, diff review, or manual validation>

- [ ] Step 2: <short action title>
  Why: ...
  Files: ...
  Change: ...
  End result: ...
  Verify: ...
```

## Step Content

For every step, include:

- **Why**: Tie the task back to a requirement, risk, dependency, or review need.
- **Files**: Name exact paths whenever known. If a path is uncertain, give the search term or module to inspect.
- **Change**: Describe the concrete code/config/test/doc change. Avoid vague verbs like "handle", "fix", or "update" unless followed by precise details.
- **End result**: State what should be true after only this step is complete.
- **Verify**: Give the smallest useful validation: a unit test, scoped E2E pattern, lint/build command, manual UI check, or diff sanity check.

## Granularity Guide

Split a task when:

- It touches unrelated layers, such as backend DTOs and frontend rendering.
- It mixes behavior change with formatting, cleanup, or test repair.
- It would be hard to review without first understanding another change.
- It has a different verification method from the surrounding work.
- It depends on a decision that may change.

Merge tasks when:

- Separating them would produce non-working intermediate code.
- The change is only meaningful as one small coherent diff.
- The same file edit and same verification cover both changes.

## Completeness Checklist

Before finalizing the plan, make sure it includes:

- Implementation steps for every accepted requirement.
- Test or validation steps for changed behavior.
- Cleanup or review-readiness steps when useful.
- Any migration, config, dependency, or rollout concerns.
- Explicit open questions only if they block execution.

## Tone

Be direct and practical. The plan should read like something an engineer can execute without needing to reconstruct the reasoning from the earlier conversation.
