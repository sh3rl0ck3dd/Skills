---
name: post-plan-code-check
description: Use after Codex has implemented a plan or code change and needs to check implementation quality before final response. Verifies duplicate/reusable code, best file placement, local project style, minimal diff, API compatibility, and consistent logging/error handling; patches Codex-owned issues when safe.
---

# Post-plan Code Check

## Overview

Run a review-readiness pass after implementing a plan. The goal is to make the code look like it belongs in the project and avoid avoidable review feedback: duplicated helpers, wrong file placement, style drift, unrelated refactors, API breakage, and inconsistent logging or error handling.

This skill is for code Codex just changed. If the user explicitly requested review-only or no file changes, report findings without editing.

## Workflow

1. Restate the implemented intent in one sentence and identify the changed files.
2. Search before accepting new code:
   - Use `rg` to look for similar functions, classes, helpers, constants, tests, request/response shapes, and error/log patterns.
   - If a similar function already exists, prefer reusing it, extending it, or overloading it when that is idiomatic for the language and compatible with existing callers.
   - Do not add a new abstraction just to avoid a small amount of local duplication unless the project already uses that pattern.
3. Verify placement:
   - Check whether the code belongs in the file/module Codex changed.
   - Compare nearby ownership boundaries, package/module names, call sites, and existing tests.
   - Move Codex-owned code only when the better location is clear from the project structure.
4. Verify local style:
   - Match nearby function shape, naming, loop style, null/empty checks, comments, imports, exception handling, and test structure.
   - Match existing logging style: logger choice, level, message shape, placeholders, included identifiers, and whether errors include stack traces.
   - Match existing error handling: exception type, returned error model, status code, fallback behavior, and user-facing message style.
5. Check review-readiness gates:
   - Keep the diff minimal and tied to the implemented plan.
   - Remove unrelated refactors, formatting churn, debug prints, temporary comments, and dead code.
   - Preserve public API, schema, route, config, and behavior compatibility unless the accepted plan explicitly required a breaking change.
   - Ensure tests or verification match the risk and changed behavior.

## Fix Policy

- Patch issues Codex introduced when the fix is local, low risk, and clearly follows existing project patterns.
- Do not silently rewrite user-owned changes, broad module structure, public APIs, generated files, or behavior outside the accepted plan.
- If a finding is ambiguous or risky, stop and report the finding with the file path, why it matters, and the recommended fix.

## Final Response

Keep the final response short and concrete:

- Say what was checked.
- Say what was patched, if anything.
- Mention remaining risks or verification that could not be run.
