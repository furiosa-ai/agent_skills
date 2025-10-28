#!/usr/bin/env python3
"""
Unified diff analyzer for commit messages and PR restructuring.

Usage:
    # Analyze staged changes (for commit message)
    python analyze_diff.py --staged [--json] [--allow-large]

    # Analyze PR range (for history restructuring or PR creation)
    python analyze_diff.py <base_commit> [--json] [--allow-large]

Features:
- Smart fallback for large diffs (>5000 lines)
- Three-tier strategy: full diff, additions only, or error
- Unified output format

Output (JSON):
    {
        "diff": "...",
        "diff_type": "full|additions_only|full_forced",
        "stats": {"insertions": X, "deletions": Y, "files_changed": Z},
        "files": ["..."],  // staged mode only
        "base_branch": "...",  // range mode only
        "current_commits": [...],  // range mode only
        "backup_command": "...",  // range mode only
        "warning": "...",  // optional
        "error": "..."  // optional (exits with code 1)
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


def handle_large_diff(total_insertions, total_deletions, files_changed, diff_cmd, allow_large):
    """Handle large diffs with three-tier strategy.

    Returns: dict with diff, diff_type, stats, and optional warning/error
    """
    total_lines = total_insertions + total_deletions
    THRESHOLD = 5000

    # Case 1: Normal size - full diff
    if total_lines <= THRESHOLD:
        diff = run_git_command(diff_cmd)
        return {
            "diff": diff if diff else "",
            "diff_type": "full",
            "stats": {
                "insertions": total_insertions,
                "deletions": total_deletions,
                "files_changed": files_changed
            }
        }

    # Case 2: Large total, but additions acceptable - additions only
    if total_insertions <= THRESHOLD:
        # Get only additions (added lines, new files)
        additions_cmd = diff_cmd + " --diff-filter=AM"
        diff = run_git_command(additions_cmd)
        return {
            "diff": diff if diff else "",
            "diff_type": "additions_only",
            "warning": f"Large diff ({total_lines} lines). Showing additions only ({total_insertions}+). Deletions ({total_deletions}-) omitted.",
            "stats": {
                "insertions": total_insertions,
                "deletions": total_deletions,
                "files_changed": files_changed
            }
        }

    # Case 3: Even additions too large
    if not allow_large:
        return {
            "error": "large_diff",
            "message": f"Large diff: {total_insertions}+ additions exceeds threshold ({THRESHOLD}).",
            "suggestion": "Split into smaller changes or use --allow-large to force full analysis.",
            "stats": {
                "insertions": total_insertions,
                "deletions": total_deletions,
                "files_changed": files_changed
            }
        }

    # Case 4: Forced large diff
    diff = run_git_command(diff_cmd)
    return {
        "diff": diff if diff else "",
        "diff_type": "full_forced",
        "warning": f"⚠️ Forced large diff analysis ({total_lines} lines). May exceed context limits.",
        "stats": {
            "insertions": total_insertions,
            "deletions": total_deletions,
            "files_changed": files_changed
        },
        "forced": True
    }


def get_staged_diff(allow_large=False):
    """Get staged changes for commit message generation."""
    # Check if there are staged changes
    staged_files = run_git_command("git diff --cached --name-only")
    if not staged_files:
        return {"error": "no_staged_changes", "message": "No staged changes. Use 'git add' to stage files."}

    # Get statistics
    stats_output = run_git_command("git diff --cached --numstat")

    # Parse stats
    files = []
    total_insertions = 0
    total_deletions = 0

    if stats_output:
        for line in stats_output.split('\n'):
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                insertions = int(parts[0]) if parts[0] != '-' and parts[0].isdigit() else 0
                deletions = int(parts[1]) if parts[1] != '-' and parts[1].isdigit() else 0
                filename = parts[2]

                files.append(filename)
                total_insertions += insertions
                total_deletions += deletions

    # Handle large diff
    result = handle_large_diff(
        total_insertions,
        total_deletions,
        len(files),
        "git diff --cached",
        allow_large
    )

    # Add files list for staged mode
    if "error" not in result:
        result["files"] = files

    return result


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


def get_range_diff(base_branch, allow_large=False):
    """Get diff from base to HEAD for PR analysis."""
    # Get statistics
    stats_output = run_git_command(f"git diff {base_branch}..HEAD --numstat")

    # Parse stats
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

    # Get current branch
    current_branch = get_current_branch()

    # Get commit history (for reference)
    commits = get_commit_history(base_branch)

    if not commits:
        return {
            "error": "no_commits",
            "message": f"No commits found between {base_branch} and {current_branch}"
        }

    # Handle large diff
    result = handle_large_diff(
        total_insertions,
        total_deletions,
        files_changed,
        f"git diff {base_branch}..HEAD",
        allow_large
    )

    # Add range-specific fields
    if "error" not in result:
        result["base_branch"] = base_branch
        result["current_branch"] = current_branch
        result["current_commits"] = commits

        # Generate backup command
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_branch = f"backup/{current_branch}-{timestamp}"
        result["backup_command"] = f"git branch {backup_branch}"
        result["restore_command"] = f"git reset --hard {backup_branch}"

    return result


def main():
    """Main entry point."""
    output_json = '--json' in sys.argv
    allow_large = '--allow-large' in sys.argv
    is_staged = '--staged' in sys.argv

    # Remove flags from args
    args = [arg for arg in sys.argv[1:] if arg not in ['--json', '--allow-large', '--staged']]

    # Determine mode
    if is_staged:
        # Staged mode
        result = get_staged_diff(allow_large=allow_large)
    else:
        # Range mode - requires base branch
        if not args:
            error_msg = "Base commit required for range mode. Usage: python analyze_diff.py <base_commit> [--json] [--allow-large]\nOr use --staged for staged changes."
            if output_json:
                print(json.dumps({"error": "missing_base", "message": error_msg}))
            else:
                print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)

        base_branch = args[0]
        result = get_range_diff(base_branch, allow_large=allow_large)

    # Handle errors
    if "error" in result:
        if output_json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result.get('message', result['error'])}", file=sys.stderr)
            if "suggestion" in result:
                print(f"\nSuggestion: {result['suggestion']}", file=sys.stderr)
            if "stats" in result:
                print(f"\nStats:", file=sys.stderr)
                print(f"  Files: {result['stats']['files_changed']}", file=sys.stderr)
                print(f"  Lines: +{result['stats']['insertions']} -{result['stats']['deletions']}", file=sys.stderr)
        sys.exit(1)

    # Show warning if present (not in JSON mode)
    if "warning" in result and not output_json:
        print(f"⚠️  {result['warning']}", file=sys.stderr)

    # Output result
    if output_json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        mode = "Staged Changes" if is_staged else "PR Analysis"
        print(f"=== {mode} ===")
        print(f"\nStats: +{result['stats']['insertions']} -{result['stats']['deletions']} ({result['stats']['files_changed']} files)")
        print(f"Diff type: {result.get('diff_type', 'unknown')}")

        if is_staged and "files" in result:
            print(f"\nFiles ({len(result['files'])}):")
            for f in result['files']:
                print(f"  - {f}")

        if not is_staged:
            print(f"\nBase: {result.get('base_branch')}")
            print(f"Current: {result.get('current_branch')}")
            print(f"Commits: {len(result.get('current_commits', []))}")
            if "backup_command" in result:
                print(f"\n⚠️  Backup command: {result['backup_command']}")

        print(f"\n=== Diff ===")
        print(result['diff'])


if __name__ == "__main__":
    main()
