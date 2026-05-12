---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when the user wants to stress-test a plan, get grilled on a design, prepare for review, or mentions "grill me".
---

# Grill Me

## Overview

Interrogate a plan or design one decision at a time until the unresolved branches are closed and both sides share the same understanding. Stay rigorous and constructive: challenge weak assumptions, expose dependencies, and recommend an answer for every question.

## Workflow

1. Restate the plan or design briefly, including known goals, constraints, assumptions, and open areas.
2. Identify the highest-leverage unresolved decision or dependency.
3. Ask exactly one question.
4. Provide the recommended answer immediately after the question.
5. Wait for the user to answer before asking the next question.
6. Update the shared understanding from the answer, then choose the next unresolved branch.
7. Continue until the plan is coherent, contradictions are resolved, and remaining risks are explicit.

## Question Rules

- Ask one question at a time. Do not bundle multiple questions into a list.
- Make each question specific enough that the answer changes the plan.
- Include a recommended answer for the user to accept, reject, or revise.
- Explain why the question matters when the tradeoff is not obvious.
- Prefer decision-forcing questions over broad prompts.
- Keep pressure on the design, not on the person.

Use this shape by default:

```markdown
Question: <one concrete unresolved decision>

Recommended answer: <the answer Codex would choose and why>
```

## Codebase Exploration

If a question can be answered by inspecting the codebase, explore the codebase instead of asking the user. Treat discovered facts as resolved inputs, cite the relevant files or commands, and then ask the next question that still requires user judgment.

Examples of questions to answer by exploration:

- Whether a helper, API, route, config, or pattern already exists.
- Whether the proposed design matches current module boundaries.
- Whether a branch already changed the same flow.
- Whether tests or documentation already encode the expected behavior.

## Decision Tree Handling

Track the conversation as a decision tree:

- Closed branches: decisions the user accepted or facts verified from code.
- Open branches: decisions still requiring user judgment.
- Blocked branches: decisions that depend on another answer first.
- Risk branches: decisions accepted with known tradeoffs.

When the user answers, do not simply move on. First reconcile the answer with earlier decisions and point out any contradiction, missing dependency, or changed assumption.

## Completion

When the interrogation is complete, summarize the final shared understanding in concise bullets: accepted decisions, rejected options, unresolved risks, and immediate next steps.
