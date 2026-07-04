# Safety Rules

> **Read this before ANY destructive action in Phase 4.**

## Golden Rule

**Never lose the user's data. If you cannot verify safety, stop and ask.**

---

## Pre-Action Checklist

For every file or directory you plan to delete, move, or modify:

### 1. User Authorization
- [ ] The user explicitly approved this specific action in this conversation
- [ ] The approval is not stale (from a previous session or different context)
- [ ] If the user said "clean up X" but didn't specify exactly what, present findings and ASK before acting

### 2. Identity Verification
- [ ] The target path still exists and matches what was approved
- [ ] The file/directory has not been modified since the plan was made
- [ ] You are NOT about to delete a different file with a similar name

### 3. Git Safety (for project directories)
- [ ] Unpushed commits are backed up: `git branch backup/pre-archive-YYYYMMDD && git push origin backup/pre-archive-YYYYMMDD`
- [ ] Untracked files are reviewed — some may be valuable local-only files
- [ ] Regenerable content (`node_modules/`, `.venv/`) is stripped before archiving

### 4. Collision Check (for moves)
- [ ] The destination path does not already exist
- [ ] If it exists, the user has decided whether to merge, overwrite, or rename

### 5. Critical Path Protection
- [ ] NEVER touch: `~/.ssh/`, `~/.gitconfig`, `~/.zshrc`, `~/.profile`, `~/.zshenv`
- [ ] NEVER touch: `~/.config/` (contains shell, git, and tool configs)
- [ ] NEVER touch: `~/Library/` (macOS system — use system tools only)
- [ ] NEVER touch: `~/.Trash/` (system-managed)

---

## Risk Levels

### ZERO RISK — No confirmation needed beyond initial plan approval
- Empty directories (`rmdir` only, never `rm -rf` on non-empty paths)
- `.DS_Store` files
- Cache directories (`.cache/`, `__pycache__/`, `.pytest_cache/`)
- `node_modules/`, `.venv/`, `venv/` — always regenerable
- `.pyc` files

### LOW RISK — Confirm once, execute in batch
- Stale backup files (`.bak`, `.backup`, `.save`) when live version exists
- Dotfiles for uninstalled CLI tools (verified via `classify_dotfiles.py`)
- Old app versions when current version is verified installed
- DMG/packages when the installed app is verified at `/Applications/`

### MEDIUM RISK — Confirm individually
- Duplicate files — verify checksums match before deleting one copy
- Old project directories — check git state, push backup branch first
- Configuration files — read and confirm they contain no unique data

### HIGH RISK — Always open a conversation
- Any file in `~/Documents/` with personal/sensitive content
- Database files (`.sqlite`, `.db`)
- SSH keys, certificates, credential files
- Anything the user has edited in the last 7 days

---

## Recovery

If something goes wrong:

1. **Git repos**: Cloned from GitHub — can be re-cloned. Archived repos have backup branches.
2. **Trash**: macOS Trash (`~/.Trash/`) might still have the file. Check before it's emptied.
3. **Time Machine**: If enabled, previous versions are recoverable.
4. **Regenerable content**: `node_modules`, `.venv` — just run `npm install` or `pip install`.

---

## Scripts That Enforce Safety

| Script | Safety mechanism |
|---|---|
| `clean_dsstore.py` | Dry-run by default, `--execute` to actually delete |
| `strip_regenerable.py` | Dry-run by default, `--execute` to remove |
| `check_git_state.py` | Read-only — never modifies anything |
| `find_duplicates.py` | Read-only — reports duplicates, never deletes |
| `classify_dotfiles.py` | Read-only — reports classification, never removes |
