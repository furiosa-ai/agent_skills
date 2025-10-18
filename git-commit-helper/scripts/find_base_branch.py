#!/usr/bin/env python3
"""
Find base branch candidates for current HEAD.

Analyzes all remote branches and finds merge-bases with HEAD,
ranking them by number of commits (closer is better).

Usage:
    python find_base_branch.py [--json] [--limit N]

Arguments:
    --json: Output in JSON format
    --limit: Number of candidates to show (default: 5)

Output (human-readable):
    Found 5 base branch candidates:

    1. origin/refactor/aten-infrastructure-improvements
       Base: 078889590a (Refactor ATen ops tests...)
       Commits: 1

    2. origin/master
       Base: 99cafb6bc3 (Merge #14774)
       Commits: 6

Output (JSON):
    {
      "candidates": [
        {
          "rank": 1,
          "branch": "origin/refactor/aten-infrastructure-improvements",
          "base_commit": "078889590abab2c1799c2643894606501c124d82",
          "base_commit_short": "078889590a",
          "base_commit_message": "Refactor ATen ops tests...",
          "commit_count": 1
        }
      ],
      "current_branch": "refactor/aten-macro-refactoring"
    }
"""

import subprocess
import sys
import json
from datetime import datetime


def run_git_command(cmd):
    """Execute git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_remote_branches():
    """
    Get list of master/main branches from all remotes.
    """
    output = run_git_command("git branch -r")
    if not output:
        return []

    branches = []
    for line in output.split('\n'):
        branch = line.strip()
        # Skip HEAD pointers
        if '->' in branch or not branch:
            continue

        # Only include master or main branches
        if branch.endswith('/master') or branch.endswith('/main'):
            branches.append(branch)

    return branches


def get_merge_base(branch, head="HEAD"):
    """Get merge base between branch and HEAD."""
    return run_git_command(f"git merge-base {branch} {head} 2>/dev/null")


def get_commit_count(base, head="HEAD"):
    """Get number of commits from base to HEAD."""
    count_str = run_git_command(f"git rev-list --count {base}..{head} 2>/dev/null")
    return int(count_str) if count_str and count_str.isdigit() else None


def get_commit_info(commit_sha):
    """Get commit message for a SHA."""
    # Get short message (first line only)
    msg = run_git_command(f"git show -s --format=%s {commit_sha} 2>/dev/null")
    return msg if msg else "Unknown commit"


def get_current_branch():
    """Get current branch name."""
    return run_git_command("git rev-parse --abbrev-ref HEAD")


def find_base_candidates(limit=5):
    """
    Find base branch candidates ranked by commit count.

    Returns list of candidates, each with:
    - branch: remote branch name
    - base_commit: full SHA of merge-base
    - base_commit_short: short SHA (10 chars)
    - base_commit_message: commit message
    - commit_count: number of commits from base to HEAD
    """
    branches = get_remote_branches()
    candidates = []

    for branch in branches:
        merge_base = get_merge_base(branch)
        if not merge_base:
            continue

        commit_count = get_commit_count(merge_base)
        if commit_count is None:
            continue

        commit_msg = get_commit_info(merge_base)

        candidates.append({
            "branch": branch,
            "base_commit": merge_base,
            "base_commit_short": merge_base[:10],
            "base_commit_message": commit_msg,
            "commit_count": commit_count
        })

    # Sort by commit count (ascending) - closer bases first
    candidates.sort(key=lambda x: x["commit_count"])

    # Add rank
    for i, candidate in enumerate(candidates[:limit], 1):
        candidate["rank"] = i

    return candidates[:limit]


def format_human_readable(candidates, current_branch):
    """Format output for human reading."""
    lines = []
    lines.append(f"Current branch: {current_branch}")
    lines.append(f"\nFound {len(candidates)} base branch candidate(s):\n")

    for candidate in candidates:
        lines.append(f"{candidate['rank']}. {candidate['branch']}")
        lines.append(f"   Base: {candidate['base_commit_short']} ({candidate['base_commit_message']})")
        lines.append(f"   Commits: {candidate['commit_count']}")
        lines.append("")

    return '\n'.join(lines)


def main():
    """Main entry point."""
    output_json = '--json' in sys.argv
    limit = 5

    # Parse --limit argument
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--limit' and i + 2 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 2])
            except ValueError:
                pass

    current_branch = get_current_branch()
    candidates = find_base_candidates(limit)

    if not candidates:
        error_msg = "No base branch candidates found"
        if output_json:
            print(json.dumps({"error": error_msg}))
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)

    if output_json:
        result = {
            "current_branch": current_branch,
            "candidates": candidates
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_human_readable(candidates, current_branch))


if __name__ == "__main__":
    main()
