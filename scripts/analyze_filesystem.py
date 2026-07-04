#!/usr/bin/env python3
"""Map and size a filesystem tree. Produces a size-ranked inventory.

Usage:
    python analyze_filesystem.py ~/Developer              # single dir
    python analyze_filesystem.py ~/Developer ~/Documents  # multiple
    python analyze_filesystem.py ~/ --max-depth 3 --min-size 10M
"""

import argparse
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_size(path: Path) -> int:
    """Fast size calculation using st_size for files, recursive walk for dirs."""
    try:
        if path.is_file() or path.is_symlink():
            return path.stat().st_size
        total = 0
        for entry in path.iterdir():
            try:
                if entry.is_file() or entry.is_symlink():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_size(entry)
            except (PermissionError, OSError):
                pass
        return total
    except (PermissionError, OSError):
        return 0


def format_size(size: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def parse_size(s: str) -> int:
    """Parse human-readable size like '100MB' to bytes."""
    s = s.strip().upper()
    multipliers = {'B': 1, 'K': 1024, 'KB': 1024, 'M': 1024**2,
                   'MB': 1024**2, 'G': 1024**3, 'GB': 1024**3}
    for suffix, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if s.endswith(suffix):
            return int(float(s[:-len(suffix)]) * mult)
    return int(s)


def analyze(root: str, max_depth: int | None = None,
            min_size: int = 0, exclude: list[str] | None = None) -> list[dict]:
    """Walk a directory tree and return size-ranked inventory."""
    exclude = exclude or []
    root_path = Path(root).expanduser().resolve()
    results = []

    # Collect all directories first
    dirs_to_scan = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_depth = len(Path(dirpath).relative_to(root_path).parts)
        if max_depth is not None and current_depth >= max_depth:
            dirnames.clear()
            continue
        # Filter excluded patterns
        dirnames[:] = [d for d in dirnames if d not in exclude and not d.startswith('.') or d in ('.git', '.claude', '.github')]
        dirs_to_scan.append(Path(dirpath))

    # Size directories in parallel
    entries = []
    # Add files at root level and large files
    for entry in root_path.iterdir():
        try:
            entries.append(entry)
        except PermissionError:
            pass

    # Size all entries
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(get_size, e): e for e in entries + dirs_to_scan}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                size = future.result()
                if size >= min_size:
                    results.append({
                        'path': str(entry),
                        'name': entry.name,
                        'type': 'directory' if entry.is_dir() else 'file',
                        'size_bytes': size,
                        'size_human': format_size(size),
                    })
            except Exception:
                pass

    results.sort(key=lambda x: x['size_bytes'], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Map and size a filesystem tree.")
    parser.add_argument('paths', nargs='+', help='Directories to analyze')
    parser.add_argument('--max-depth', type=int, help='Maximum directory depth')
    parser.add_argument('--min-size', type=str, default='0',
                        help='Minimum size to report (e.g., 10MB, 1GB)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    min_size = parse_size(args.min_size) if args.min_size else 0
    all_results = []

    for path in args.paths:
        all_results.extend(analyze(path, args.max_depth, min_size))

    # Global sort
    all_results.sort(key=lambda x: x['size_bytes'], reverse=True)

    if args.json:
        import json
        print(json.dumps(all_results, indent=2))
    else:
        print(f"{'SIZE':>10}  {'TYPE':<10}  PATH")
        print("-" * 80)
        for r in all_results:
            print(f"{r['size_human']:>10}  {r['type']:<10}  {r['path']}")


if __name__ == '__main__':
    main()
