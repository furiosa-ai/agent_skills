#!/usr/bin/env python3
"""
Reply to a GitHub PR comment with automatic Claude Code signature.

Usage:
    python3 reply_to_comment.py <owner> <repo> <comment_id> --body "Reply message" [--json]

Examples:
    python3 reply_to_comment.py furiosa-ai agent_skills 123456 \\
        --body "Thanks for the feedback!" --json

    python3 reply_to_comment.py owner repo 789012 \\
        --body "I've updated the documentation"

Requires:
    - gh CLI installed and authenticated
    - Python 3.6+
"""

import sys
import json
import subprocess
import argparse


CLAUDE_SIGNATURE = "\n\n---\n🤖 *Updated by Claude Code*"


def post_reply(owner, repo, comment_id, body):
    """
    Post a reply to a PR comment using GitHub REST API.

    Automatically adds Claude Code signature to the reply.

    Returns:
        dict: Parsed JSON response with reply information
    """
    # Add Claude signature
    body_with_signature = body + CLAUDE_SIGNATURE

    cmd = [
        'gh', 'api',
        '-X', 'POST',
        f'repos/{owner}/{repo}/pulls/comments/{comment_id}/replies',
        '-f', f'body={body_with_signature}'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to post reply to comment {comment_id}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse API response", file=sys.stderr)
        print(f"Response: {result.stdout}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Reply to a GitHub PR comment with Claude Code signature'
    )
    parser.add_argument('owner', help='Repository owner')
    parser.add_argument('repo', help='Repository name')
    parser.add_argument('comment_id', help='Comment ID to reply to')
    parser.add_argument('--body', required=True, help='Reply message body')
    parser.add_argument('--json', action='store_true', help='Output JSON format')

    args = parser.parse_args()

    # Post reply
    response = post_reply(args.owner, args.repo, args.comment_id, args.body)

    # Extract key information
    reply_id = response.get('id', '')
    reply_url = response.get('html_url', '')

    # Output
    if args.json:
        output = {
            'success': True,
            'comment_id': args.comment_id,
            'reply_id': reply_id,
            'reply_url': reply_url
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"✓ Successfully posted reply to comment {args.comment_id}")
        print(f"  Reply ID: {reply_id}")
        print(f"  Reply URL: {reply_url}")
        print()
        print("Your reply:")
        print(f"  {args.body}")
        print(CLAUDE_SIGNATURE)

    sys.exit(0)


if __name__ == '__main__':
    main()
