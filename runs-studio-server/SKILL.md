---
name: runs-studio-server
description: >-
    Run the user's local Graph Studio server reset/start workflow exactly as defined:
    remove Docker containers, delete Studio logs, run Gradle clean and broker mock,
    attach to tmux session gs, restart the frontend watch task, detach without stopping it,
    and start the Studio server. Use when the user asks to run studio-server,
    reset Studio server, restart Graph Studio local server, or follow the runs-studio-server workflow.
---

# Runs Studio Server

## Purpose

Run the user's local Studio server workflow in the exact order below. Preserve the commands as written unless the user explicitly changes a step.

Default wait timeout: 45 seconds, except where a step defines a different wait.

## Operating Rules

- Run steps in order.
- Do not invent replacement commands for the user's commands.
- If a command needs elevated permission, request approval in the normal Codex way.
- If a wait condition is not met within the timeout, stop and report the last useful output or state.
- Treat destructive steps as destructive and summarize what they will remove before running them.
- Step 7 and Step 8 happen inside tmux session `gs`.
- Step 9 happens after detaching from tmux, back in the normal terminal.

## Workflow

### Step 1: Remove Docker Containers

Command:

```bash
docker rm -f $(docker ps -aq)
```

Completion state:

- Wait for the command to complete.
- Print or report all closed container IDs emitted by the command.

Notes:

- This removes all Docker containers returned by `docker ps -aq`.
- If there are no containers, handle the no-op case cleanly and continue only if the command outcome is acceptable.

### Step 2: Remove Studio Build Logs

Command:

```bash
sudo rm -r /scratch/rajarash/graph-cloud/studio/build/logs/
```

Completion state:

- Wait for the command to complete.

### Step 3: Remove Studio Logs

Command:

```bash
sudo rm -r /scratch/rajarash/graph-cloud/studio/logs/
```

Completion state:

- Wait for the command to complete.

### Step 4: Clean Gradle Build

Command:

```bash
./gradlew clean
```

Completion state:

- Wait until terminal output contains `BUILD SUCCESSFUL`.

### Step 5: Start Broker Mock

Command:

```bash
./gradlew broker-mock:startServer
```

Completion state:

- Wait until terminal output contains `BUILD SUCCESSFUL`.

### Step 6: Attach to Tmux

Command:

```bash
tmux attach -t gs
```

Completion state:

- Tmux session `gs` opens.

### Step 7: Stop Existing Gradle Task Inside Tmux

Command:

```text
Ctrl+C
```

Completion state:

- If a Gradle task is already running, wait until the last running command exits.
- Control should return inside tmux before continuing.

### Step 8: Start Frontend Watch Inside Tmux, Then Detach

Command:

```bash
./gradlew :studio:watchFrontendDev
```

Completion state:

- Wait 30 seconds.
- Detach from tmux with `Ctrl+B`, then `D`.
- Leave the frontend watch task and tmux session running.

### Step 9: Start Studio Server In Normal Terminal

Command:

```bash
./gradlew --no-daemon studio:startServer
```

Completion state:

- Wait until terminal output contains `BUILD SUCCESSFUL`.

## Execution Guidance

Use PTY sessions for interactive steps:

- Use a normal shell session for Steps 1-5.
- Use an interactive PTY session for Step 6.
- Send keys into the tmux-attached PTY for Steps 7-8.
- After detaching from tmux, continue in the normal terminal for Step 9.

Before Step 9, verify that the tmux session was detached rather than killed when possible.
