# Categorization Guide

How to classify every finding from Phase 1 into actionable categories for Phase 2.

---

## Category 1: Empty Artifacts

**What**: Directories with zero files, zero-byte files, empty scaffolds.

**Examples**:
- `my-app/` — empty project directory created by a scaffolding tool but never used
- `docs/knowledge-base/` — empty subdirectory in a documentation folder
- `logs/` — log directory with zero log files

**Action**: Delete. Zero risk — nothing to lose.

**Detection**:
```bash
find ~ -maxdepth 4 -type d -empty -not -path "*/Library/*" -not -path "*/.Trash/*"
```

---

## Category 2: Regenerable Cruft

**What**: Directories and files that can be recreated deterministically from source.

**Examples**:
- `node_modules/` — `npm install` or `pnpm install`
- `.venv/` / `venv/` — `python -m venv .venv && pip install -r requirements.txt`
- `__pycache__/`, `*.pyc` — Python bytecode cache
- `.pytest_cache/`, `.mypy_cache/` — tool caches
- Package manager download caches (e.g., `.pkg-cache/`, `.bundle/cache/`)
- OS installers (`.dmg`, `.pkg`, `.deb`, `.rpm`) when the installed app exists

**Action**: Delete. Regenerable = safe. Strip from project archives before archiving.

**Detection**: `scripts/strip_regenerable.py`

---

## Category 3: Stale Backups

**What**: Backup copies where the live version still exists and the backup is clearly old.

**Examples**:
- `config.json.backup` — live `config.json` exists and is newer
- `.zshrc.save` — live `.zshrc` exists
- `settings.json.bak` — live `settings.json` exists

**Action**: Delete. If the live version is intact, the backup adds no value.

**Caution**: If the live version does NOT exist, the backup is the ONLY copy. Never delete in that case.

---

## Category 4: Orphaned Tool Data

**What**: Dotfiles and directories for tools that are no longer installed.

**Examples**:
- `~/.old-cli/` — CLI tool removed months ago
- `~/.config/legacy-editor/` — editor replaced by a newer alternative
- `~/.agent-app/` — agent runtime moved to a remote server

**Action**: Delete. The tool is gone; its config and caches serve no purpose.

**Detection**: `scripts/classify_dotfiles.py` — look for `"status": "orphaned"`

**Caution**: Some tools store user data (not just config) in their dotdirs. Check contents before deleting:
```bash
du -sh ~/.tool-name/
ls -la ~/.tool-name/
```

---

## Category 5: Old App Versions

**What**: Previous versions of an application that has been upgraded or replaced.

**Examples**:
- `~/.OldIDE/` + `/Applications/OldIDE.app` — replaced by `~/.NewIDE/`
- Extension directories with old version numbers (e.g., `plugin-0.5.0` when `plugin-1.2.0` exists)
- Duplicate application installs at different paths

**Action**: Delete old version AFTER verifying the new version is installed and functional.

**Detection**: Manual — look for sibling directories with version numbers or dated names.

---

## Category 6: Duplicate Files

**What**: Files with identical content (same checksum) but different names or locations.

**Examples**:
- `resume-final.pdf` and `resume-final-v2.pdf` — identical content, confusing names
- `logo.png` in both `~/downloads/` and `~/documents/assets/`
- Backup copies that were copied to a second location

**Action**: Keep one copy, delete the rest. Choose the one with the clearest name and canonical location.

**Detection**: `scripts/find_duplicates.py`

---

## Category 7: Project Iterations

**What**: Multiple directories representing the same project at different rename points or versions.

**Examples**:
- `old-app-name/` → renamed to `new-app-name/` — both directories still exist
- `project-v1/` and `project-v2/` — v2 is the active version, v1 is stale
- A project that was moved from one directory to another, with the original left behind

**Action**:
1. Identify the active (current) version — check git remote, last modified date, package names
2. For old versions: push backup branch if unpushed, then archive
3. Rename the active version if needed to match the current name

**Detection**: Check package.json names and git remote URLs:
```bash
cat project/package.json | jq .name
cd project && git remote -v
```

---

## Category 8: Misplaced Files

**What**: Files in the wrong directory — documents in downloads, configs at filesystem root, secrets mixed with code.

**Examples**:
- Resume PDFs in `~/downloads/` — should be in a documents folder
- API key JSON files at the home directory root
- Setup guides and configuration notes mixed with project source code

**Action**: Move to the correct location. Create target directories as needed.

---

## Proposed Directory Structures

These are templates — adapt names to your own workflow and conventions.

### Projects directory (e.g., `~/projects/` or `~/Developer/`)
```
projects/
├── active-app/            ← active projects, flat list
├── open-source-lib/
├── secrets/               ← API keys, OAuth JSONs, env files
├── _backups/              ← design docs, reference snapshots
└── _archive/              ← old projects (after git backup)
```

### Documents directory (e.g., `~/documents/` or `~/Documents/`)
```
documents/
├── personal/
│   ├── resumes/
│   ├── finance/
│   ├── legal/
│   └── education/
├── work/
│   ├── client-a/
│   ├── freelance/
│   └── presentations/
├── projects/
│   ├── project-alpha/
│   └── project-beta/
├── secrets/               ← credentials, API console exports
└── archive/
```

### Downloads directory
Rule: If it's been in downloads more than ~2 weeks, file it or delete it.
- Installers → delete if app is installed
- PDFs → file in documents
- Images → file in pictures or documents
- Code files → move to appropriate project
