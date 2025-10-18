#!/usr/bin/env python3
"""
Extract staged changes for commit message generation.

Usage:
    python analyze_staged.py [--json]

Output (JSON):
    {
        "files": ["file1.js", "file2.py"],
        "stats": {"insertions": 45, "deletions": 12, "files_changed": 3},
        "diff": "full diff content..."
    }
"""

import subprocess
import sys
import json


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
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_staged_info():
    """Get staged diff and statistics."""
    # Check if there are staged changes
    staged_files = run_git_command("git diff --cached --name-only")
    if not staged_files:
        return None

    # Get full diff
    diff = run_git_command("git diff --cached")

    # Get statistics
    stats_output = run_git_command("git diff --cached --numstat")

    # Parse stats
    files = []
    total_insertions = 0
    total_deletions = 0

    for line in stats_output.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            insertions = int(parts[0]) if parts[0] != '-' else 0
            deletions = int(parts[1]) if parts[1] != '-' else 0
            filename = parts[2]

            files.append(filename)
            total_insertions += insertions
            total_deletions += deletions

    return {
        "files": files,
        "stats": {
            "insertions": total_insertions,
            "deletions": total_deletions,
            "files_changed": len(files)
        },
        "diff": diff
    }


def main():
    """Main entry point."""
    output_json = '--json' in sys.argv

    # Get staged information
    info = get_staged_info()

    if info is None:
        if output_json:
            print(json.dumps({"error": "No staged changes found"}))
        else:
            print("No staged changes. Use 'git add' to stage files.", file=sys.stderr)
        sys.exit(1)

    # Output
    if output_json:
        print(json.dumps(info, indent=2))
    else:
        # Human-readable output
        print("=== Staged Changes ===")
        print(f"\nFiles ({info['stats']['files_changed']}):")
        for f in info['files']:
            print(f"  - {f}")
        print(f"\nStats: +{info['stats']['insertions']} -{info['stats']['deletions']}")
        print(f"\n=== Diff ===")
        print(info['diff'])


if __name__ == "__main__":
    main()
