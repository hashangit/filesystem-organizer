#!/usr/bin/env python3
"""Identify and optionally remove regenerable directories and files.

Targets: node_modules/, .venv/, venv/, __pycache__/, *.pyc, .pytest_cache/

Usage:
    python strip_regenerable.py ~/Developer              # Dry run — list only
    python strip_regenerable.py ~/Developer --execute    # Actually remove
    python strip_regenerable.py ~ --dry-run --json       # JSON output
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REGENERABLE_DIRS = {
    'node_modules', '.venv', 'venv', '__pycache__',
    '.pytest_cache', '.mypy_cache', '.tox', '.eggs',
    'dist', 'build', '*.egg-info',
}

REGENERABLE_FILES = {'.pyc', '.pyo'}

SKIP_PATHS = {
    str(Path.home() / 'Library'),
    str(Path.home() / '.Trash'),
}


def format_size(size: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def get_dir_size(path: Path) -> int:
    """Fast recursive size calculation."""
    try:
        total = 0
        for entry in path.iterdir():
            try:
                if entry.is_file() or entry.is_symlink():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry)
            except (PermissionError, OSError):
                pass
        return total
    except (PermissionError, OSError):
        return 0


def find_regenerable(root: str, max_depth: int = 5) -> list[dict]:
    """Find all regenerable directories and files under root."""
    root_path = Path(root).expanduser().resolve()
    root_str = str(root_path)

    if any(root_str.startswith(p) for p in SKIP_PATHS):
        return []

    results = []

    for dirpath, dirnames, _ in os.walk(root_path):
        current_depth = len(Path(dirpath).relative_to(root_path).parts)
        if current_depth >= max_depth:
            dirnames.clear()
            continue

        dp = Path(dirpath)
        for d in list(dirnames):
            if d in REGENERABLE_DIRS:
                full_path = dp / d
                size = get_dir_size(full_path)
                results.append({
                    'path': str(full_path),
                    'type': 'directory',
                    'kind': d,
                    'size_bytes': size,
                    'size_human': format_size(size),
                })
                dirnames.remove(d)  # Don't recurse into it

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Find and optionally remove regenerable directories.")
    parser.add_argument('paths', nargs='+', help='Directories to scan')
    parser.add_argument('--execute', action='store_true',
                        help='Actually delete (default: dry run)')
    parser.add_argument('--max-depth', type=int, default=5,
                        help='Maximum scan depth')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    all_findings = []
    for path in args.paths:
        all_findings.extend(find_regenerable(path, args.max_depth))

    all_findings.sort(key=lambda x: x['size_bytes'], reverse=True)
    total_size = sum(f['size_bytes'] for f in all_findings)

    if args.json:
        output = {
            'total_size_bytes': total_size,
            'total_size_human': format_size(total_size),
            'count': len(all_findings),
            'findings': all_findings,
        }
        print(json.dumps(output, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"REGENERABLE CONTENT SCAN")
    print(f"{'='*60}")
    print(f"  Found: {len(all_findings)} items ({format_size(total_size)})")
    print()

    if not all_findings:
        print("  Nothing found.")
        return

    for f in all_findings[:20]:
        print(f"  {f['size_human']:>10}  {f['kind']:<20}  {f['path']}")
    if len(all_findings) > 20:
        print(f"  ... and {len(all_findings) - 20} more")

    if args.execute:
        deleted = 0
        failed = 0
        for f in all_findings:
            try:
                shutil.rmtree(f['path'])
                deleted += 1
            except OSError as e:
                print(f"  Failed: {f['path']} — {e}")
                failed += 1
        print(f"\n  Deleted: {deleted}, Failed: {failed}")
        print(f"  Recovered: {format_size(total_size)}")
    else:
        print(f"\n  DRY RUN — run with --execute to remove.")
        print(f"  These can all be regenerated (npm install, pip install, etc.)")


if __name__ == '__main__':
    main()
