#!/usr/bin/env python3
"""
Analyze PR changes and suggest commit restructuring strategy.

IMPORTANT: Only the final diff (base..HEAD) matters. Intermediate commits
are for reference only. The restructuring should reflect the final state.

Usage:
    python suggest_commits.py [base_branch] [--json]

Arguments:
    base_branch: Branch to compare against (default: auto-detect from origin/HEAD)

Output (JSON):
    {
        "base_branch": "main",
        "current_branch": "feature/auth",
        "total_diff": "FINAL diff from base to HEAD (this is the truth)",
        "stats": {"insertions": 45, "deletions": 12, "files_changed": 3},
        "current_commits": [
            {
                "hash": "abc123",
                "message": "Add user validation",
                "files": ["auth.js"],
                "stats": {"insertions": 10, "deletions": 2}
            }
        ],
        "backup_command": "git branch backup/feature-auth-20250118-143022"
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
    except subprocess.CalledProcessError as e:
        return None


def get_all_remotes():
    """Get list of all git remotes."""
    output = run_git_command("git remote")
    return output.split('\n') if output else []


def branch_exists(branch_name):
    """Check if a branch exists."""
    return run_git_command(f"git rev-parse --verify {branch_name} 2>/dev/null") is not None


def get_merge_base(base, head):
    """Get merge base between two refs."""
    return run_git_command(f"git merge-base {base} {head} 2>/dev/null")


def get_commit_timestamp(commit):
    """Get commit timestamp as integer."""
    timestamp = run_git_command(f"git show -s --format=%ct {commit} 2>/dev/null")
    return int(timestamp) if timestamp else 0


def get_default_branch():
    """Find most recent merge-base across all remotes."""
    remotes = get_all_remotes()
    most_recent_timestamp = 0
    most_recent_base = None

    for remote in remotes:
        for branch in ['master', 'main']:
            remote_branch = f"{remote}/{branch}"
            if branch_exists(remote_branch):
                merge_base = get_merge_base(remote_branch, "HEAD")
                if merge_base:
                    timestamp = get_commit_timestamp(merge_base)
                    if timestamp > most_recent_timestamp:
                        most_recent_timestamp = timestamp
                        most_recent_base = merge_base

    return most_recent_base


def get_current_branch():
    """Get current branch name."""
    return run_git_command("git rev-parse --abbrev-ref HEAD")


def get_commit_history(base_branch):
    """Get commit history from base to HEAD (for reference only)."""
    log_format = "--pretty=format:%H%x00%s%x00%an%x00%ae"
    log_output = run_git_command(f"git log {base_branch}..HEAD {log_format}")

    if not log_output:
        return []

    commits = []
    for line in log_output.split('\n'):
        if not line.strip():
            continue

        parts = line.split('\x00')
        if len(parts) >= 4:
            commit_hash = parts[0]
            message = parts[1]
            author_name = parts[2]
            author_email = parts[3]

            # Get files changed in this commit
            files_output = run_git_command(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
            files_list = [f for f in files_output.split('\n') if f.strip()] if files_output else []

            # Get stats for this commit
            stats_output = run_git_command(f"git diff-tree --no-commit-id --numstat -r {commit_hash}")
            insertions = 0
            deletions = 0
            if stats_output:
                for stat_line in stats_output.split('\n'):
                    if not stat_line.strip():
                        continue
                    stat_parts = stat_line.split('\t')
                    if len(stat_parts) >= 2:
                        insertions += int(stat_parts[0]) if stat_parts[0].isdigit() else 0
                        deletions += int(stat_parts[1]) if stat_parts[1].isdigit() else 0

            commits.append({
                "hash": commit_hash[:7],
                "message": message,
                "author": f"{author_name} <{author_email}>",
                "files": files_list,
                "stats": {
                    "insertions": insertions,
                    "deletions": deletions
                }
            })

    return commits


def get_total_diff(base_branch):
    """Get FINAL diff from base to HEAD (this is the source of truth)."""
    diff = run_git_command(f"git diff {base_branch}..HEAD")
    stats_output = run_git_command(f"git diff {base_branch}..HEAD --numstat")

    # Parse total stats
    total_insertions = 0
    total_deletions = 0
    files_changed = 0

    if stats_output:
        for line in stats_output.split('\n'):
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                total_insertions += int(parts[0]) if parts[0].isdigit() else 0
                total_deletions += int(parts[1]) if parts[1].isdigit() else 0
                files_changed += 1

    return {
        "diff": diff if diff else "",
        "stats": {
            "insertions": total_insertions,
            "deletions": total_deletions,
            "files_changed": files_changed
        }
    }


def generate_backup_command(current_branch):
    """Generate backup branch command for safety."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_branch = f"backup/{current_branch}-{timestamp}"
    return f"git branch {backup_branch}"


def main():
    """Main entry point."""
    output_json = '--json' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--json']

    # Determine base branch
    if args:
        base_branch = args[0]
    else:
        base_branch = get_default_branch()
        if base_branch is None:
            error_msg = "Could not detect default branch. Please specify: python suggest_commits.py <base_branch>"
            if output_json:
                print(json.dumps({"error": error_msg}))
            else:
                print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)

    # Get current branch
    current_branch = get_current_branch()

    # Get commit history (for reference)
    commits = get_commit_history(base_branch)

    if not commits:
        error_msg = f"No commits found between {base_branch} and {current_branch}"
        if output_json:
            print(json.dumps({"error": error_msg}))
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)

    # Get FINAL diff (source of truth)
    total_diff_info = get_total_diff(base_branch)

    # Generate backup command
    backup_cmd = generate_backup_command(current_branch)

    # Build result
    result = {
        "base_branch": base_branch,
        "current_branch": current_branch,
        "total_diff": total_diff_info["diff"],
        "stats": total_diff_info["stats"],
        "current_commits": commits,
        "backup_command": backup_cmd,
        "restore_command": f"git reset --hard {backup_cmd.split()[-1]}"
    }

    # Output
    if output_json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"=== PR Analysis ===")
        print(f"Base: {base_branch}")
        print(f"Current: {current_branch}")
        print(f"\n⚠️  SAFETY: Before restructuring, create backup:")
        print(f"   {backup_cmd}")
        print(f"   Restore with: {result['restore_command']}")
        print(f"\n=== Final Changes (Source of Truth) ===")
        print(f"Total: +{result['stats']['insertions']} -{result['stats']['deletions']} ({result['stats']['files_changed']} files)")
        print(f"\n=== Current Commits ({len(commits)}) ===")
        for i, commit in enumerate(commits, 1):
            print(f"{i}. {commit['hash']} - {commit['message']}")
            print(f"   Files: {', '.join(commit['files'][:3])}")
            if len(commit['files']) > 3:
                print(f"   ... and {len(commit['files']) - 3} more")
            print(f"   Stats: +{commit['stats']['insertions']} -{commit['stats']['deletions']}")
        print(f"\n=== Final Diff ===")
        print(result['total_diff'])


if __name__ == "__main__":
    main()
