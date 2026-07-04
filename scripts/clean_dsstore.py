#!/usr/bin/env python3
"""Safe .DS_Store removal with path exclusions.

Usage:
    python clean_dsstore.py              # Dry run — lists files, no deletion
    python clean_dsstore.py --execute    # Actually delete them
    python clean_dsstore.py ~/Developer  # Scope to specific directory
"""

import argparse
import os
import sys
from pathlib import Path


# Paths that should NEVER be scanned or touched
PROTECTED_PREFIXES = [
    '/System/',
    '/Library/System/',
]

# Paths to skip during scan
SKIP_PREFIXES = [
    str(Path.home() / 'Library'),
    str(Path.home() / '.Trash'),
]

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', '.venv', 'venv', '__pycache__'}


def find_ds_store_files(root: str, max_depth: int | None = None) -> list[Path]:
    """Find all .DS_Store files under root, respecting exclusions."""
    root_path = Path(root).expanduser().resolve()
    root_str = str(root_path)

    # Never scan protected paths
    if any(root_str.startswith(p) for p in PROTECTED_PREFIXES):
        print(f"Skipping protected path: {root}", file=sys.stderr)
        return []

    if any(root_str.startswith(p) for p in SKIP_PREFIXES):
        print(f"Skipping excluded path: {root}", file=sys.stderr)
        return []

    results = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_depth = len(Path(dirpath).relative_to(root_path).parts)
        if max_depth is not None and current_depth >= max_depth:
            dirnames.clear()
            continue

        # Skip unwanted directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        if '.DS_Store' in filenames:
            results.append(Path(dirpath) / '.DS_Store')

    return results


def main():
    parser = argparse.ArgumentParser(description="Safe .DS_Store cleanup.")
    parser.add_argument('paths', nargs='*', default=[str(Path.home())],
                        help='Directories to scan (default: home)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually delete files (default: dry run)')
    parser.add_argument('--max-depth', type=int, help='Maximum scan depth')
    args = parser.parse_args()

    all_files = []
    for path in args.paths:
        all_files.extend(find_ds_store_files(path, args.max_depth))

    total_size = sum(f.stat().st_size for f in all_files if f.exists())

    if args.execute:
        deleted = 0
        for f in all_files:
            try:
                f.unlink()
                deleted += 1
            except OSError as e:
                print(f"Failed: {f} — {e}", file=sys.stderr)
        print(f"Deleted {deleted} .DS_Store files "
              f"({total_size / 1024:.1f} KB recovered)")
    else:
        print(f"DRY RUN — {len(all_files)} .DS_Store files found "
              f"({total_size / 1024:.1f} KB)")
        if all_files:
            print(f"\nRun with --execute to delete them.")
            # Show first 10
            for f in all_files[:10]:
                print(f"  {f}")
            if len(all_files) > 10:
                print(f"  ... and {len(all_files) - 10} more")


if __name__ == '__main__':
    main()
