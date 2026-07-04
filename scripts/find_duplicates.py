#!/usr/bin/env python3
"""Find duplicate files by checksum comparison within specified directories.

Usage:
    python find_duplicates.py ~/Downloads
    python find_duplicates.py ~/Documents ~/Developer --min-size 1MB
"""

import argparse
import hashlib
import os
from pathlib import Path
from collections import defaultdict


def parse_size(s: str) -> int:
    s = s.strip().upper()
    multipliers = {'B': 1, 'K': 1024, 'KB': 1024, 'M': 1024**2,
                   'MB': 1024**2, 'G': 1024**3, 'GB': 1024**3}
    for suffix, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if s.endswith(suffix):
            return int(float(s[:-len(suffix)]) * mult)
    return int(s)


def format_size(size: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def file_hash(path: Path, chunk_size: int = 65536) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return ""


def find_duplicates(paths: list[str], min_size: int = 0,
                    exclude_patterns: list[str] | None = None) -> list[dict]:
    """Find files with identical checksums. Two-pass: size filter, then hash."""
    exclude_patterns = exclude_patterns or []
    # Pass 1: group by size
    by_size: dict[int, list[Path]] = defaultdict(list)
    for scan_path in paths:
        root = Path(scan_path).expanduser().resolve()
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                fpath = Path(dirpath) / fname
                # Skip excluded patterns
                if any(pat in str(fpath) for pat in exclude_patterns):
                    continue
                try:
                    size = fpath.stat().st_size
                    if size >= min_size:
                        by_size[size].append(fpath)
                except OSError:
                    pass

    # Pass 2: hash files with duplicate sizes
    groups = []
    for size, files in by_size.items():
        if len(files) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for f in files:
            h = file_hash(f)
            if h:
                by_hash[h].append(f)
        for h, dupes in by_hash.items():
            if len(dupes) > 1:
                groups.append({
                    'hash': h,
                    'size_bytes': size,
                    'size_human': format_size(size),
                    'count': len(dupes),
                    'files': sorted(str(d) for d in dupes),
                    'wasted_bytes': size * (len(dupes) - 1),
                    'wasted_human': format_size(size * (len(dupes) - 1)),
                })

    groups.sort(key=lambda g: g['wasted_bytes'], reverse=True)
    return groups


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files by checksum.")
    parser.add_argument('paths', nargs='+', help='Directories to scan')
    parser.add_argument('--min-size', type=str, default='0',
                        help='Minimum file size (e.g., 1MB)')
    parser.add_argument('--exclude', nargs='*', default=['node_modules', '.git', '.venv', '__pycache__'],
                        help='Directory patterns to exclude')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    min_size = parse_size(args.min_size)
    groups = find_duplicates(args.paths, min_size, args.exclude)

    if args.json:
        import json
        print(json.dumps(groups, indent=2))
    else:
        total_wasted = sum(g['wasted_bytes'] for g in groups)
        print(f"Found {len(groups)} duplicate groups "
              f"(wasting {format_size(total_wasted)})\n")

        for g in groups:
            print(f"[{g['size_human']}] {g['count']} identical files (hash: {g['hash'][:12]}…)")
            for f in g['files']:
                print(f"    {f}")
            print()


if __name__ == '__main__':
    main()
