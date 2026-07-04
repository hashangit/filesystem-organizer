#!/usr/bin/env python3
"""Cross-reference home dotdirs against installed applications and CLI tools.

Usage:
    python classify_dotfiles.py
    python classify_dotfiles.py --json
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_installed_brew_formulae() -> set[str]:
    try:
        result = subprocess.run(['brew', 'list', '--formula'], capture_output=True, text=True, timeout=10)
        return set(result.stdout.strip().split('\n')) if result.returncode == 0 else set()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def get_installed_brew_casks() -> set[str]:
    try:
        result = subprocess.run(['brew', 'list', '--cask'], capture_output=True, text=True, timeout=10)
        return set(result.stdout.strip().split('\n')) if result.returncode == 0 else set()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def get_applications() -> set[str]:
    apps = set()
    for apps_dir in ['/Applications', os.path.expanduser('~/Applications')]:
        if os.path.isdir(apps_dir):
            for entry in os.listdir(apps_dir):
                if entry.endswith('.app'):
                    apps.add(entry.replace('.app', '').lower())
    return apps


def get_path_binaries() -> set[str]:
    binaries = set()
    for path_dir in os.environ.get('PATH', '').split(':'):
        if os.path.isdir(path_dir):
            for entry in os.listdir(path_dir):
                binaries.add(entry.lower())
    return binaries


def get_npm_globals() -> set[str]:
    try:
        result = subprocess.run(['npm', 'list', '-g', '--depth=0', '--json'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return set(data.get('dependencies', {}).keys())
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return set()


KNOWN_DOTDIRS = {
    '.claude': {'names': ['claude', 'claude-code'], 'type': 'cli'},
    '.codex': {'names': ['codex', 'openai-codex'], 'type': 'cli'},
    '.gemini': {'names': ['gemini', 'gemini-cli'], 'type': 'cli'},
    '.cursor': {'names': ['cursor'], 'type': 'app'},
    '.docker': {'names': ['docker'], 'type': 'cli'},
    '.npm': {'names': ['npm'], 'type': 'cli'},
    '.nvm': {'names': ['nvm'], 'type': 'cli'},
    '.rustup': {'names': ['rustup', 'rust'], 'type': 'cli'},
    '.bun': {'names': ['bun'], 'type': 'cli'},
    '.oh-my-zsh': {'names': ['oh-my-zsh', 'zsh'], 'type': 'shell'},
    '.vim': {'names': ['vim'], 'type': 'cli'},
    '.vnc': {'names': ['vnc', 'tigervnc', 'realvnc'], 'type': 'cli'},
    '.supabase': {'names': ['supabase'], 'type': 'cli'},
    '.convex': {'names': ['convex'], 'type': 'cli'},
    '.bundle': {'names': ['bundle', 'bundler', 'ruby'], 'type': 'cli'},
    '.npmrc': {'names': ['npm'], 'type': 'cli'},
    '.homebrew': {'names': ['homebrew', 'brew'], 'type': 'system'},
    '.vagrant': {'names': ['vagrant'], 'type': 'cli'},
    '.terraform': {'names': ['terraform'], 'type': 'cli'},
    '.aws': {'names': ['aws', 'aws-cli'], 'type': 'cli'},
    '.gcloud': {'names': ['gcloud', 'google-cloud-sdk'], 'type': 'cli'},
    '.kube': {'names': ['kubectl', 'kubernetes'], 'type': 'cli'},
    '.cargo': {'names': ['cargo', 'rust'], 'type': 'cli'},
    '.conda': {'names': ['conda', 'anaconda'], 'type': 'cli'},
    '.pyenv': {'names': ['pyenv'], 'type': 'cli'},
    '.rbenv': {'names': ['rbenv'], 'type': 'cli'},
    '.goenv': {'names': ['goenv'], 'type': 'cli'},
    '.jenv': {'names': ['jenv'], 'type': 'cli'},
    '.sdkman': {'names': ['sdkman', 'sdk'], 'type': 'cli'},
    '.android': {'names': ['android', 'android-studio'], 'type': 'cli'},
    '.gradle': {'names': ['gradle'], 'type': 'cli'},
    '.m2': {'names': ['maven', 'mvn'], 'type': 'cli'},
    '.ivy2': {'names': ['sbt', 'ivy'], 'type': 'cli'},
    '.wakatime': {'names': ['wakatime'], 'type': 'cli'},
    '.pencil': {'names': ['pencil', 'pencildev'], 'type': 'extension'},
    '.dual-graph': {'names': ['dual-graph', 'graperoot'], 'type': 'cli'},
    '.zcode': {'names': ['zcode'], 'type': 'cli'},
    '.kilocode': {'names': ['kilo', 'kilo-code', 'kilocode'], 'type': 'extension'},
    '.commandcode': {'names': ['commandcode'], 'type': 'cli'},
    '.superpowers-mcp': {'names': ['superpowers'], 'type': 'cli'},
    '.cmuxterm': {'names': ['cmux'], 'type': 'cli'},
    '.omp': {'names': ['omp'], 'type': 'cli'},
    '.zai': {'names': ['zai'], 'type': 'cli'},
    '.pi': {'names': ['pi'], 'type': 'cli'},
    '.mcp-auth': {'names': ['mcp'], 'type': 'system'},
    '.agent-browser': {'names': ['agent-browser'], 'type': 'cli'},
    '.pkg-cache': {'names': ['pkg'], 'type': 'cache'},
    '.antigravity': {'names': ['antigravity'], 'type': 'app'},
    '.antigravity-ide': {'names': ['antigravity-ide'], 'type': 'app'},
    '.hermes': {'names': ['hermes', 'hermes-agent'], 'type': 'cli'},
    '.roomodes': {'names': ['roo', 'roocode'], 'type': 'extension'},
    '.seepient': {'names': ['seepient'], 'type': 'cli'},
}

def classify_dotfile(name: str, installed: dict) -> dict:
    """Classify a single dotfile/dotdir as active, orphaned, or system."""
    # System dotfiles — always keep
    system_names = {'.CFUserTextEncoding', '.DS_Store', '.Trash', '.Cache',
                    '.zshrc', '.zprofile', '.zshenv', '.profile',
                    '.zsh_history', '.bash_history', '.gitconfig', '.ssh',
                    '.config', '.local'}
    if name in system_names:
        return {'name': name, 'status': 'system', 'reason': 'System or shell-critical file'}

    # Zsh completion dumps — system
    if name.startswith('.zcompdump'):
        return {'name': name, 'status': 'system', 'reason': 'Zsh completion cache'}

    known = KNOWN_DOTDIRS.get(name)
    if not known:
        return {'name': name, 'status': 'unknown',
                'reason': 'No known tool mapping — investigate manually'}

    if known['type'] in ('system', 'shell', 'cache'):
        return {'name': name, 'status': 'system', 'reason': 'System infrastructure'}

    names_to_check = [n.lower() for n in known['names']] + [name.lstrip('.').lower()]
    found_in = []

    if known['type'] == 'app':
        if any(n in installed['applications'] for n in names_to_check):
            found_in.append('Applications')
    elif known['type'] == 'cli':
        if any(n in installed['path_binaries'] for n in names_to_check):
            found_in.append('PATH')
        if any(n in installed['brew_formulae'] for n in names_to_check):
            found_in.append('Homebrew formula')
        if any(n in installed['brew_casks'] for n in names_to_check):
            found_in.append('Homebrew cask')
        if any(n in installed['npm_globals'] for n in names_to_check):
            found_in.append('npm global')
    elif known['type'] == 'extension':
        if any(n in installed['applications'] for n in names_to_check):
            found_in.append('Applications')

    if found_in:
        return {'name': name, 'status': 'active',
                'reason': f"Found in: {', '.join(found_in)}"}
    else:
        return {'name': name, 'status': 'orphaned',
                'reason': f"Tool '{known['names'][0] if known['names'] else name}' is not installed"}


def main():
    import argparse as ap
    parser = ap.ArgumentParser(description="Classify dotfiles against installed tools.")
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    installed = {
        'brew_formulae': get_installed_brew_formulae(),
        'brew_casks': get_installed_brew_casks(),
        'applications': get_applications(),
        'path_binaries': get_path_binaries(),
        'npm_globals': get_npm_globals(),
    }

    home = Path.home()
    dotfiles = [e.name for e in home.iterdir() if e.name.startswith('.')]

    results = [classify_dotfile(d, installed) for d in sorted(dotfiles)]
    active = [r for r in results if r['status'] == 'active']
    orphaned = [r for r in results if r['status'] == 'orphaned']
    system_files = [r for r in results if r['status'] == 'system']
    unknown = [r for r in results if r['status'] == 'unknown']

    if args.json:
        print(json.dumps({
            'active': active, 'orphaned': orphaned,
            'system': system_files, 'unknown': unknown
        }, indent=2))
    else:
        print(f"\n{'='*60}")
        print("DOTFILE CLASSIFICATION")
        print(f"{'='*60}")
        print(f"\n  Active:     {len(active)} — tool is installed")
        print(f"  Orphaned:   {len(orphaned)} — tool NOT installed")
        print(f"  System:     {len(system_files)} — critical, never remove")
        print(f"  Unknown:    {len(unknown)} — investigate manually")

        for label, items in [("ORPHANED — safe to remove", orphaned),
                              ("UNKNOWN — investigate before removing", unknown)]:
            if items:
                print(f"\n{'─'*60}")
                print(label)
                print(f"{'─'*60}")
                for r in items:
                    print(f"  {r['name']:<30} {r['reason']}")

        if active:
            print(f"\n{'─'*60}")
            print("ACTIVE — do not remove")
            print(f"{'─'*60}")
            for r in active:
                print(f"  {r['name']:<30} {r['reason']}")
        print()


if __name__ == '__main__':
    main()
