#!/usr/bin/env python3
"""Create a compact PR diff index for guided PR walkthroughs.

The script is intentionally dependency-free so Codex can run it inside most repos.
It reports changed files and hunk line anchors relative to a merge base.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


HUNK_RE = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\s?(.*)$"
)


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    section: str
    added_lines: list[int]
    deleted_old_lines: list[int]

    @property
    def added_ranges(self) -> str:
        return compress_ranges(self.added_lines)

    @property
    def deleted_ranges(self) -> str:
        return compress_ranges(self.deleted_old_lines)


@dataclass
class ChangedFile:
    path: str
    status: str
    old_path: str | None
    hunks: list[Hunk]


@dataclass
class DiffIndex:
    repo_root: str
    base_ref: str
    head_ref: str
    merge_base: str
    files: list[ChangedFile]


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n{proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def git(args: list[str], cwd: Path | None = None, check: bool = True) -> str:
    return run(["git", *args], cwd=cwd, check=check)


def repo_root() -> Path:
    out = git(["rev-parse", "--show-toplevel"]).strip()
    if not out:
        raise RuntimeError("not inside a git repository")
    return Path(out)


def ref_exists(ref: str, cwd: Path) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=str(cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def choose_base(user_base: str | None, cwd: Path) -> str:
    candidates: list[str] = []
    if user_base:
        candidates.append(user_base)
    for env_name in ("PR_BASE", "BASE_BRANCH"):
        env_val = os.getenv(env_name)
        if env_val:
            candidates.append(env_val)
    candidates.extend(["origin/main", "origin/master", "main", "master", "develop", "dev"])

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if ref_exists(candidate, cwd):
            return candidate
    raise RuntimeError(
        "could not find a base ref. pass --base, for example: --base origin/main"
    )


def merge_base(base: str, head: str, cwd: Path) -> str:
    out = git(["merge-base", head, base], cwd=cwd, check=False).strip()
    if out:
        return out
    # Fallback for unusual histories where the supplied base is already a commit-ish.
    if ref_exists(base, cwd):
        return git(["rev-parse", base], cwd=cwd).strip()
    raise RuntimeError(f"could not determine merge base between {head!r} and {base!r}")


def parse_name_status(text: str) -> dict[str, ChangedFile]:
    files: dict[str, ChangedFile] = {}
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status_code = parts[0]
        status = status_code[0]
        if status == "R" and len(parts) >= 3:
            old_path, new_path = parts[1], parts[2]
            files[new_path] = ChangedFile(
                path=new_path, status=status_code, old_path=old_path, hunks=[]
            )
        elif status == "C" and len(parts) >= 3:
            old_path, new_path = parts[1], parts[2]
            files[new_path] = ChangedFile(
                path=new_path, status=status_code, old_path=old_path, hunks=[]
            )
        elif len(parts) >= 2:
            path = parts[1]
            files[path] = ChangedFile(path=path, status=status_code, old_path=None, hunks=[])
    return files


def current_diff_file(line: str) -> str | None:
    # diff --git a/foo b/foo
    parts = line.split(" ")
    if len(parts) < 4:
        return None
    b_path = parts[3]
    if b_path.startswith("b/"):
        return b_path[2:]
    return b_path


def parse_hunks(diff_text: str, files: dict[str, ChangedFile]) -> None:
    current_path: str | None = None
    current_hunk: Hunk | None = None
    old_line = 0
    new_line = 0

    def attach_hunk() -> None:
        nonlocal current_hunk
        if current_path and current_hunk:
            if current_path not in files:
                files[current_path] = ChangedFile(
                    path=current_path, status="?", old_path=None, hunks=[]
                )
            files[current_path].hunks.append(current_hunk)
        current_hunk = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            attach_hunk()
            current_path = current_diff_file(line)
            continue
        if line.startswith("+++ "):
            plus_path = line[4:].strip()
            if plus_path == "/dev/null":
                # Deleted file; keep the b/path from the diff header if possible.
                continue
            current_path = plus_path[2:] if plus_path.startswith("b/") else plus_path
            continue
        match = HUNK_RE.match(line)
        if match:
            attach_hunk()
            old_start = int(match.group(1))
            old_count = int(match.group(2) or "1")
            new_start = int(match.group(3))
            new_count = int(match.group(4) or "1")
            section = match.group(5).strip()
            current_hunk = Hunk(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                section=section,
                added_lines=[],
                deleted_old_lines=[],
            )
            old_line = old_start
            new_line = new_start
            continue
        if current_hunk is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current_hunk.added_lines.append(new_line)
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            current_hunk.deleted_old_lines.append(old_line)
            old_line += 1
        elif line.startswith(" "):
            old_line += 1
            new_line += 1

    attach_hunk()


def compress_ranges(nums: Iterable[int]) -> str:
    values = sorted(set(nums))
    if not values:
        return "-"
    ranges: list[str] = []
    start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev = value
            continue
        ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = value
    ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ", ".join(ranges)


def build_index(base: str | None, head: str) -> DiffIndex:
    root = repo_root()
    base_ref = choose_base(base, root)
    mb = merge_base(base_ref, head, root)
    name_status = git(
        ["diff", "--name-status", "--find-renames", f"{mb}...{head}"], cwd=root
    )
    files = parse_name_status(name_status)
    diff_text = git(
        ["diff", "--unified=0", "--find-renames", f"{mb}...{head}"], cwd=root
    )
    parse_hunks(diff_text, files)
    ordered_files = list(files.values())
    return DiffIndex(
        repo_root=str(root),
        base_ref=base_ref,
        head_ref=head,
        merge_base=mb,
        files=ordered_files,
    )


def status_label(status: str) -> str:
    first = status[0] if status else "?"
    return {
        "A": "added",
        "M": "modified",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "?": "changed",
    }.get(first, status)


def to_markdown(index: DiffIndex) -> str:
    lines: list[str] = []
    short_mb = index.merge_base[:12]
    lines.append("# PR diff index")
    lines.append("")
    lines.append(f"- repo: `{index.repo_root}`")
    lines.append(f"- base: `{index.base_ref}`")
    lines.append(f"- head: `{index.head_ref}`")
    lines.append(f"- merge base: `{short_mb}`")
    lines.append(f"- changed files: `{len(index.files)}`")
    lines.append("")
    if not index.files:
        lines.append("No changed files found.")
        return "\n".join(lines)

    lines.append("## Changed files and line anchors")
    lines.append("")
    for idx, file in enumerate(index.files, 1):
        old = f" (from `{file.old_path}`)" if file.old_path else ""
        lines.append(f"### {idx}. `{file.path}` — {status_label(file.status)}{old}")
        if not file.hunks:
            lines.append("- no textual hunks detected")
            lines.append("")
            continue
        for hunk_idx, hunk in enumerate(file.hunks, 1):
            section = f" — {hunk.section}" if hunk.section else ""
            new_anchor = hunk.added_ranges
            old_anchor = hunk.deleted_ranges
            if new_anchor != "-":
                lines.append(f"- hunk {hunk_idx}: new line(s) `{new_anchor}`{section}")
            elif old_anchor != "-":
                lines.append(f"- hunk {hunk_idx}: deleted old line(s) `{old_anchor}`{section}")
            else:
                lines.append(
                    f"- hunk {hunk_idx}: new range `{hunk.new_start}` with no added-line anchor{section}"
                )
        lines.append("")
    lines.append("## How to use this index")
    lines.append("")
    lines.append(
        "Pick the first runtime boundary from the list, then inspect the first meaningful changed line in that file. "
        "Use `nl -ba <file> | sed -n 'START,ENDp'` to open surrounding context."
    )
    return "\n".join(lines)


def to_json(index: DiffIndex) -> str:
    return json.dumps(asdict(index), indent=2, sort_keys=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="base ref or branch, such as origin/main")
    parser.add_argument("--head", default="HEAD", help="head ref to compare, default: HEAD")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        index = build_index(args.base, args.head)
    except Exception as exc:  # noqa: BLE001 - show concise CLI error to Codex/user.
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(to_json(index))
    else:
        print(to_markdown(index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
