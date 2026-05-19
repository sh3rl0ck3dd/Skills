---
name: restart-studio-server
description: >-
    Restart the user's local Graph Studio server with the lightweight workflow:
    stop/remove exactly one running Docker container for the Graph Studio server
    image, then run `./gradlew --no-daemon studio:startServer` and wait for the
    server readiness signal. Use when the user asks to restart Studio server,
    restart Graph Studio backend, rerun `studio:startServer`, or use the smaller
    restart flow instead of the full `runs-studio-server` reset workflow.
---

# Restart Studio Server

## Purpose

Run the user's lightweight Graph Studio server restart workflow. This is intentionally smaller than `runs-studio-server`: do not clear all Docker containers, remove logs, run Gradle clean, start broker mock, or touch tmux/frontend watch unless the user explicitly asks.

Default wait timeout: 120 seconds, except where a command needs more time and the user explicitly allows it.

## Operating Rules

- Run from `/scratch/rajarash/graph-cloud` unless the user gives another repo path.
- Do not remove arbitrary Docker containers.
- Only target a running container whose image is exactly or clearly the Graph Studio server image:

```text
iad.ocir.io/ogcs/ogcs-docker-stage-local/adbs-graph/graph-studio-server:MAIN
```

- If zero matching containers are running, stop and report that no Graph Studio server container was found.
- If multiple matching containers are running, stop and show the matching container IDs, names, and images; ask the user which one to remove.
- If a command needs elevated permission, request approval in the normal Codex way.
- If the server readiness signal is not seen within the timeout, stop and report the last useful output or state.

## Workflow

### Step 1: Find the Studio Server Container

Command:

```bash
docker ps --filter "ancestor=iad.ocir.io/ogcs/ogcs-docker-stage-local/adbs-graph/graph-studio-server:MAIN" --format "{{.ID}}\t{{.Image}}\t{{.Names}}"
```

Completion state:

- Exactly one line means one matching running container was found; continue to Step 2.
- No output means there is no running Studio server container; stop and report that no matching container was found.
- More than one line means multiple matching containers exist; stop and ask the user which one to remove.

### Step 2: Remove the Matching Container

Command shape:

```bash
docker rm -f <container-id>
```

Completion state:

- Wait for the command to complete.
- Report the removed container ID.

### Step 3: Start Studio Server

Command:

```bash
./gradlew --no-daemon studio:startServer
```

Completion state:

- Wait until output contains `GraphStudio is ready to rock!`.
- If that readiness line is not visible but Gradle prints `BUILD SUCCESSFUL`, treat the Gradle task as successful and report that the explicit readiness line was not observed.
- Keep the command session running if `studio:startServer` is a foreground server process; do not send Ctrl+C unless the user asks to stop it.

## Reporting

- Say whether a container was removed, no matching container was found, or multiple matches made the target ambiguous.
- Say whether the readiness signal was observed.
- Include the local Studio URLs if `studio:startServer` prints them.
