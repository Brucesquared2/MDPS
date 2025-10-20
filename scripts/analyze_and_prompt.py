#!/usr/bin/env python3
"""
Run linters/tests, detect problems that need human input, and interactively prompt the developer
so they can fix hunks in VS Code before committing/pushing.

Usage:
  - Run manually from repo root:
      python scripts/analyze_and_prompt.py
  - The script will:
      * run ruff (if installed) and capture output
      * run mypy (if installed) and capture output
      * run unit tests (python -m unittest discover) if configured
      * run PowerShell ScriptAnalyzer via pwsh if available for .ps1 files
      * scan repo files for TODO/FIXME/NEEDS-CLARITY markers and parse linter errors that look like ParseError/TerminatorExpectedAtEndOfString
      * present items that require developer choices (open file in VS Code, auto-fix if supported, skip, or input replacement)
"""

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

RE_QUESTIONABLE = re.compile(r"\b(TODO|FIXME|NEEDS[-_ ]CLARITY|REVIEW|ASK):?", re.IGNORECASE)
RE_PARSE_ERRORS = re.compile(r"(TerminatorExpectedAtEndOfString|ParseError|Traceback|SyntaxError)", re.IGNORECASE)
ROOT = Path.cwd()

def run_cmd(cmd: List[str], capture: bool = True, check: bool = False) -> Tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=capture, text=True, check=False)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out
    except FileNotFoundError:
        return 127, f"Command not found: {cmd[0]}"

def run_linters() -> str:
    out_all = []
    # ruff
    rc, out = run_cmd(["ruff", "."], capture=True)
    if rc == 127:
        out_all.append("ruff not found (skip). Install with `pip install ruff` to enable.")
    else:
        out_all.append("--- ruff output ---\n" + out)
    # mypy
    rc, out = run_cmd(["mypy", "."], capture=True)
    if rc == 127:
        out_all.append("mypy not found (skip). Install with `pip install mypy` to enable.")
    else:
        out_all.append("--- mypy output ---\n" + out)
    return "\n".join(out_all)

def run_tests() -> str:
    rc, out = run_cmd([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "*.py"], capture=True)
    if rc == 0:
        return "--- tests passed ---\n" + out
    else:
        return f"--- tests exited {rc} ---\n" + out

def run_powershell_analyzer() -> str:
    # Will attempt to run PSScriptAnalyzer via pwsh (PowerShell Core) if available and .ps1 files exist
    ps_files = list(ROOT.rglob("*.ps1"))
    if not ps_files:
        return "No PowerShell files found; skipping PSScriptAnalyzer."
    rc, out = run_cmd(["pwsh", "-NoProfile", "-Command", "Import-Module PSScriptAnalyzer; Invoke-ScriptAnalyzer -Path . -Recurse | Out-String"], capture=True)
    if rc == 127:
        return "pwsh or PSScriptAnalyzer not available; skipping PS analysis."
    return "--- PSScriptAnalyzer output ---\n" + out

def scan_for_markers() -> List[Tuple[Path, int, str]]:
    findings = []
    for path in ROOT.rglob("*.*"):
        if path.is_file() and path.suffix in {".py", ".ps1", ".sh", ".psm1"}:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if RE_QUESTIONABLE.search(line):
                    findings.append((path, i, line.strip()))
    return findings

def extract_parse_issues(text: str) -> List[str]:
    items = []
    for line in text.splitlines():
        if RE_PARSE_ERRORS.search(line):
            items.append(line)
    return items

def prompt_choice(prompt: str, options: List[str]) -> str:
    opts = "/".join(options)
    while True:
        choice = input(f"{prompt} ({opts}): ").strip().lower()
        if not choice and "enter" in options:
            return "enter"
        if choice in options:
            return choice
        print("Invalid choice:", choice)

def open_in_vscode(path: Path, line: int = 1) -> None:
    # Open file in VS Code at a line (if 'code' CLI available)
    cmd = ["code", "-g", f"{str(path)}:{line}"]
    subprocess.run(cmd)

def main() -> int:
    print("Running linters/tests... this may take a moment.")
    linters_out = run_linters()
    tests_out = run_tests()
    ps_out = run_powershell_analyzer()

    parse_issues = extract_parse_issues(linters_out + "\n" + tests_out + "\n" + ps_out)
    markers = scan_for_markers()

    if parse_issues:
        print("\nParse / error issues detected:")
        for i, it in enumerate(parse_issues, start=1):
            print(f"{i}. {it}")
        print("\nThese often require manual fixes before proceeding.")
        choice = prompt_choice("Open repo in VS Code now to edit files (recommended)?", ["y", "n"])
        if choice == "y":
            # Open repo root
            subprocess.run(["code", str(ROOT)])
            print("Opened VS Code. Fix parse errors and re-run this script when ready.")
            return 2
        return 1

    if markers:
        print("\nFound markers that may need clarifications (TODO/FIXME/NEEDS-CLARITY):")
        for idx, (path, line, snippet) in enumerate(markers, start=1):
            print(f"{idx}. {path}:{line}: {snippet}")
        for path, line, snippet in markers:
            print("\n---")
            print(f"File: {path} Line: {line}")
            print(snippet)
            action = prompt_choice("Choose action: open/edit/skip/auto-fix (open/edit/skip/auto)", ["open", "edit", "skip", "auto"])
            if action == "open":
                open_in_vscode(path, line)
                input("Press Enter after you review/edit the file in VS Code to continue...")
            elif action == "edit":
                print("Please paste the replacement text for this line (single-line). Press Enter when done.")
                repl = input("> ")
                txt = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                if 1 <= line <= len(txt):
                    txt[line - 1] = repl
                    path.write_text("\n".join(txt), encoding="utf-8")
                    print("Replaced line in file.")
            elif action == "auto":
                print("Auto-fix requested but not supported for this marker. Opening file in VS Code.")
                open_in_vscode(path, line)
                input("Press Enter after you edit the file in VS Code to continue...")
            else:
                print("Skipped.")
        # After manual handling, re-run a quick linter check
        print("\nRe-running linters to check for remaining issues...")
        rc, out = run_cmd(["ruff", "."], capture=True)
        print(out)
        print("When you're satisfied, re-run the commit or this script to continue.")
        return 0

    # No parse errors and no markers
    print("\nNo blocking parse errors or markers found. Summary outputs below.")
    print(linters_out)
    print(tests_out)
    print(ps_out)
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)