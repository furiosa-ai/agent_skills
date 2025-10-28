#!/usr/bin/env python3
"""
Fetch unresolved PR comments from GitHub using GraphQL API.

Usage:
    python3 fetch_pr_comments.py <owner> <repo> <pr_number> [--json]

Examples:
    python3 fetch_pr_comments.py furiosa-ai agent_skills 123 --json
    python3 fetch_pr_comments.py owner repo 456

Requires:
    - gh CLI installed and authenticated
    - Python 3.6+
"""

import sys
import json
import subprocess
import argparse


def fetch_unresolved_comments(owner, repo, pr_number):
    """
    Fetch unresolved PR review thread comments using GraphQL.

    Returns:
        dict: Parsed JSON response with review threads
    """
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              comments(first: 50) {
                nodes {
                  id
                  body
                  path
                  line
                  author {
                    login
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    cmd = [
        'gh', 'api', 'graphql',
        '-f', f'query={query}',
        '-F', f'owner={owner}',
        '-F', f'repo={repo}',
        '-F', f'pr={pr_number}'
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
        print(f"Error: Failed to fetch PR comments", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse GraphQL response", file=sys.stderr)
        print(f"Response: {result.stdout}", file=sys.stderr)
        sys.exit(1)


def filter_unresolved_comments(response):
    """
    Filter and extract unresolved comments from GraphQL response.

    Returns:
        list: List of comment dictionaries
    """
    try:
        threads = response['data']['repository']['pullRequest']['reviewThreads']['nodes']
    except (KeyError, TypeError) as e:
        print(f"Error: Unexpected GraphQL response structure", file=sys.stderr)
        print(f"Response: {json.dumps(response, indent=2)}", file=sys.stderr)
        sys.exit(1)

    comments = []

    for thread in threads:
        # Skip resolved threads
        if thread.get('isResolved', True):
            continue

        thread_id = thread.get('id', '')

        for comment in thread.get('comments', {}).get('nodes', []):
            comments.append({
                'comment_id': comment.get('id', ''),
                'thread_id': thread_id,
                'body': comment.get('body', ''),
                'path': comment.get('path'),
                'line': comment.get('line'),
                'author': comment.get('author', {}).get('login', 'unknown'),
                'is_resolved': False
            })

    return comments


def main():
    parser = argparse.ArgumentParser(
        description='Fetch unresolved PR comments from GitHub'
    )
    parser.add_argument('owner', help='Repository owner')
    parser.add_argument('repo', help='Repository name')
    parser.add_argument('pr_number', type=int, help='Pull request number')
    parser.add_argument('--json', action='store_true', help='Output JSON format')

    args = parser.parse_args()

    # Fetch comments
    response = fetch_unresolved_comments(args.owner, args.repo, args.pr_number)

    # Filter unresolved
    comments = filter_unresolved_comments(response)

    # Output
    if args.json:
        output = {
            'pr_number': args.pr_number,
            'unresolved_count': len(comments),
            'comments': comments
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Found {len(comments)} unresolved comment(s) in PR #{args.pr_number}")
        print()

        for i, comment in enumerate(comments, 1):
            print(f"Comment {i}:")
            print(f"  Author: {comment['author']}")
            if comment['path']:
                location = f"{comment['path']}"
                if comment['line']:
                    location += f":{comment['line']}"
                print(f"  Location: {location}")
            else:
                print(f"  Location: General PR comment")
            print(f"  Body: {comment['body'][:100]}{'...' if len(comment['body']) > 100 else ''}")
            print(f"  Comment ID: {comment['comment_id']}")
            print()

    sys.exit(0)


if __name__ == '__main__':
    main()
