#!/usr/bin/env python3
"""Audit git repositories for unpushed commits, dirty state, and untracked files.

Usage:
    python check_git_state.py ~/Developer
    python check_git_state.py ~/Developer --json
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def is_git_repo(path: Path) -> bool:
    return (path / '.git').is_dir()


def find_git_repos(root: str, max_depth: int = 3) -> list[Path]:
    """Find all git repositories under root."""
    repos = []
    root_path = Path(root).expanduser().resolve()
    for dirpath, dirnames, _ in os.walk(root_path):
        depth = len(Path(dirpath).relative_to(root_path).parts)
        if depth >= max_depth:
            dirnames.clear()
            continue
        # Skip common non-project dirs
        dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.venv', 'venv', '__pycache__', '.git')]
        if is_git_repo(Path(dirpath)):
            repos.append(Path(dirpath))
            dirnames.clear()  # Don't recurse into repos
    return repos


def check_repo(repo_path: Path) -> dict:
    """Check a single git repo for state that needs attention."""
    result = {
        'path': str(repo_path),
        'name': repo_path.name,
        'unpushed_commits': 0,
        'unpushed_log': [],
        'dirty_files': 0,
        'dirty_list': [],
        'untracked_files': 0,
        'untracked_list': [],
        'remotes': {},
        'current_branch': '',
        'needs_attention': False,
    }

    try:
        # Get remotes
        proc = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True,
                            cwd=repo_path, timeout=10)
        for line in proc.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    result['remotes'][parts[0]] = parts[1]

        # Get current branch
        proc = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True,
                            cwd=repo_path, timeout=5)
        result['current_branch'] = proc.stdout.strip()

        # Check for upstream tracking branch
        proc = subprocess.run(['git', 'rev-parse', '--abbrev-ref', '@{u}'],
                            capture_output=True, text=True, cwd=repo_path, timeout=5)
        has_upstream = proc.returncode == 0

        if has_upstream:
            # Check unpushed commits
            proc = subprocess.run(['git', 'log', '--oneline', '@{u}..HEAD'],
                                capture_output=True, text=True, cwd=repo_path, timeout=10)
            unpushed = [l for l in proc.stdout.strip().split('\n') if l]
            result['unpushed_commits'] = len(unpushed)
            result['unpushed_log'] = unpushed
        else:
            result['unpushed_commits'] = -1  # No upstream configured

        # Check dirty working tree
        proc = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True,
                            cwd=repo_path, timeout=10)
        dirty = [l for l in proc.stdout.strip().split('\n') if l]
        result['dirty_files'] = len(dirty)
        result['dirty_list'] = dirty[:50]  # Cap at 50

        # Check untracked files
        proc = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                            capture_output=True, text=True, cwd=repo_path, timeout=10)
        untracked = [l for l in proc.stdout.strip().split('\n') if l]
        result['untracked_files'] = len(untracked)
        result['untracked_list'] = untracked[:50]

        result['needs_attention'] = (
            result['unpushed_commits'] > 0 or
            result['dirty_files'] > 0 or
            result['untracked_files'] > 0
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        result['error'] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="Audit git repos for unpushed/dirty state.")
    parser.add_argument('roots', nargs='+', help='Directories to scan for git repos')
    parser.add_argument('--max-depth', type=int, default=3, help='Max scan depth')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    all_repos = []
    for root in args.roots:
        all_repos.extend(find_git_repos(root, args.max_depth))

    results = [check_repo(r) for r in all_repos]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        needs_attention = [r for r in results if r.get('needs_attention')]
        clean = [r for r in results if not r.get('needs_attention')]

        print(f"\n{'='*60}")
        print(f"GIT REPOSITORY AUDIT — {len(results)} repos found")
        print(f"{'='*60}")

        if needs_attention:
            print(f"\n  NEEDS ATTENTION ({len(needs_attention)}):")
            for r in needs_attention:
                print(f"\n  📁 {r['name']} ({r['path']})")
                print(f"     Branch: {r['current_branch']}")
                if r.get('remotes'):
                    for name, url in r['remotes'].items():
                        print(f"     Remote {name}: {url}")
                if r['unpushed_commits'] > 0:
                    print(f"     ⚠️  {r['unpushed_commits']} unpushed commits")
                    for commit in r['unpushed_log'][:5]:
                        print(f"        {commit}")
                elif r['unpushed_commits'] == -1:
                    print(f"     ⚠️  No upstream tracking branch configured")
                if r['dirty_files'] > 0:
                    print(f"     📝 {r['dirty_files']} uncommitted changes")
                if r['untracked_files'] > 0:
                    print(f"     📄 {r['untracked_files']} untracked files")
            print()

        if clean:
            print(f"  CLEAN ({len(clean)}):")
            for r in clean:
                print(f"    ✅ {r['name']}")

        print()


if __name__ == '__main__':
    main()
