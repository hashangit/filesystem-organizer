---
name: filesystem-organizer
description: >
  Comprehensive filesystem audit, cleanup, and organization. Use this skill whenever the user
  mentions organizing files, cleaning up their home directory, decluttering their system,
  finding duplicate files, archiving old projects, auditing disk usage, "where did my space go",
  "clean up my dotfiles", "organize my documents", or wants a systematic filesystem health check.
  Also use when the user says "my disk is full", "what's taking up space", "clean up old stuff",
  or mentions wanting to remove unused tools and their leftover files.
---

# Filesystem Organizer

A systematic methodology for auditing, cleaning, and organizing a user's filesystem without data loss.

## 🔴 Non-Negotiable Directive

**You MUST obtain explicit, specific user permission before ANY destructive action.**

This is absolute. There are no exceptions. You may NEVER delete, move, rename, or modify any file or directory without the user first reviewing and approving the exact change.

- Present findings. Present the plan. Wait for confirmation.
- If the user says "clean up X" without specifics, you MUST present what you found and ASK — never assume.
- The `--execute` flag on bundled scripts requires user approval before use.
- Even cache files, empty directories, and `.DS_Store` files require the user to approve the batch before deletion.

**The user's approval is the single gate between analysis and action.**

## Core Principle

**Never lose data. Never surprise the user. Always ask before destroying.**

Every destructive action requires explicit user confirmation. The skill provides analysis and a plan; the user decides what happens.

## Workflow Overview

The methodology runs in five phases. Each phase must be completed and confirmed before the next begins.

```
Phase 1: DISCOVER  → Map everything, measure sizes, find issues
Phase 2: ANALYZE   → Categorize findings, estimate savings, present plan
Phase 3: CONFIRM   → User reviews and approves the plan
Phase 4: EXECUTE   → Carry out approved changes with safety checks
Phase 5: VERIFY    → Confirm results, report savings
```

---

## Adaptive Scripting — Edit Before You Run

The bundled scripts are starting points, not finished products. **Before running any script, inspect it and adapt it to the user's system.**

### What to check and adapt

1. **`classify_dotfiles.py` — `KNOWN_DOTDIRS` mapping**: After discovering what tools and applications are on the user's system (Phase 1), add any unrecognized dotdirs to the mapping. The pre-populated list covers common tools but will never be complete. If the script reports "Unknown" entries, investigate them and add mappings so the classification is accurate for THIS user.

2. **File paths in examples and commands**: The skill uses generic paths (`~/projects/`, `~/documents/`, `~/downloads/`). Replace these with the user's actual directory names (e.g., `~/Developer/`, `~/Documents/`, `~/Downloads/` on macOS).

3. **Package manager detection**: The scripts check for Homebrew and npm by default. If the user is on Linux, adapt to use `apt`, `pacman`, `dnf`, etc. If they use `pipx`, `pnpm`, `yarn`, or other managers, extend the detection logic.

4. **User directives**: If the user gives specific instructions about what to keep, what to archive, or how to organize, update the scripts and reference files to reflect those preferences BEFORE executing.

### When to edit

- **Before Phase 1**: Update paths and package manager detection to match the user's OS
- **During Phase 1**: Add newly discovered dotdirs to `KNOWN_DOTDIRS`
- **During Phase 2**: Update `categorization_guide.md` with patterns specific to the user's workflow
- **On user directive**: If the user says "treat X as Y" or "never touch Z", codify that in the scripts immediately

---

## Phase 1: DISCOVER — Map the Filesystem

### 1.1 Start Broad

Map the top-level directory structure with sizes:

```bash
du -sh ~/projects/ ~/documents/ ~/downloads/ ~/Desktop/ ~/ 2>/dev/null
```

List all immediate children of each major directory. Separate dotfiles from regular files at home level:

```bash
find ~ -maxdepth 1 -type d -name ".*" | sort  # dotdirs
find ~ -maxdepth 1 -type f -name ".*" | sort  # dotfiles
find ~ -maxdepth 1 -type f -not -name ".*" | sort  # loose files
```

### 1.2 Find the Heavy Hitters

Identify what's consuming space. Run `scripts/analyze_filesystem.py` or use:

```bash
du -sh ~/.* ~/*/ 2>/dev/null | sort -rh | head -30
```

Pay special attention to anything >100MB — these are your primary targets.

### 1.3 Hunt for Specific Issues

Execute these checks in parallel — they're independent:

| Check | What to run |
|---|---|
| **Empty directories** | `find ~ -maxdepth 4 -type d -empty 2>/dev/null` (exclude system dirs) |
| **Duplicate files** | `scripts/find_duplicates.py` |
| **Installer/packages** | `find ~/downloads -name "*.dmg" -o -name "*.pkg" -o -name "*.deb" -o -name "*.rpm"` |
| **Loose files at root** | Check home directory and project roots for files that don't belong |
| **node_modules in wrong places** | `find ~/documents -type d -name "node_modules"` |
| **Python venvs/caches** | `find ~ -maxdepth 4 -type d \( -name ".venv" -o -name "venv" -o -name "__pycache__" \)` |
| **Backup files** | `find ~ -maxdepth 4 \( -name "*.bak" -o -name "*.backup" -o -name "*.livebackup" \)` |

### 1.4 Audit Dotfiles

Run `scripts/classify_dotfiles.py` which cross-references every `~/.<name>` directory against:
- Installed package managers (Homebrew, apt, npm, pip)
- Applications in standard install locations
- CLI tools in `$PATH`

This separates dotfiles into three buckets:
1. **Active** — tool is installed and in use
2. **Orphaned** — tool is NOT installed anywhere
3. **Unknown** — couldn't determine

### 1.5 Check Project Git State

For every project directory, run `scripts/check_git_state.py` which reports:
- Unpushed commits (ahead of remote)
- Uncommitted changes (dirty working tree)
- Untracked files
- Remote URLs

This is CRITICAL before archiving anything — unpushed work must be preserved.

---

## Phase 2: ANALYZE — Categorize and Plan

### 2.1 Categorize Every Finding

Organize discoveries into these buckets. Read `references/categorization_guide.md` for detailed examples.

| Category | Examples | Risk Level |
|---|---|---|
| **Empty artifacts** | Empty directories, zero-byte files | Zero risk |
| **Regenerable cruft** | `node_modules/`, `.venv/`, `__pycache__/`, caches, installers (if app installed) | Zero risk |
| **Stale backups** | `.bak`, `.backup`, `.save` files where live version exists | Very low |
| **Orphaned tool data** | Dotdir for uninstalled CLI, config for removed app | Low (tool gone) |
| **Old app versions** | Previous IDE install, duplicate extensions | Low (verify current version exists) |
| **Duplicate files** | Same checksum, different name/location | Medium (verify one is redundant) |
| **Project iterations** | Renamed/evolved project directories | Medium (git history check first) |
| **Misplaced files** | Documents in downloads, loose files at filesystem root | None (moves only) |

### 2.2 Estimate Savings

For each actionable finding, record the disk space it would free. Sort by impact. Present to the user as a table with:
- Item path
- Current size
- Recommended action (delete/archive/move)
- Risk level
- Justification

### 2.3 Propose Organization Structure

For the user's active directories, propose a clean layout. Reference `references/categorization_guide.md` for templates. Universal patterns:

- **Projects directory** — flat list of active projects + `secrets/` + `_backups/` + `_archive/`
- **Documents directory** — categorized: personal, work, projects, secrets, archive
- **Downloads directory** — transient; file or delete anything >2 weeks old
- **Home root** — zero loose files

---

## Phase 3: CONFIRM — User Approval

**This phase is mandatory. Never skip it.**

Present the complete plan to the user as a structured report:

1. **Summary**: total space, number of issues found, estimated savings
2. **Deletion candidates**: grouped by risk level, with justification for each
3. **Move candidates**: source → destination for each file/directory
4. **Archive plan**: which projects, git backup status
5. **Items requiring investigation**: unclear cases where you need the user's input

Use `ask` tool questions when there are genuine tradeoffs the user must decide. Never make destructive decisions unilaterally.

**The user's approval is the gate.** Nothing in Phase 4 happens until they explicitly confirm.

---

## Phase 4: EXECUTE — Carry Out Approved Changes

### 4.1 Safety Checklist (Run Before Every Destructive Action)

Read `references/safety_rules.md` for the complete checklist. At minimum, verify:

- [ ] User explicitly approved this specific action
- [ ] For git repos: unpushed commits are backed up to a branch
- [ ] For project archives: regenerable dirs (`node_modules`, `.venv`) stripped first
- [ ] For deletions: file/directory still exists and matches what was approved
- [ ] For moves: destination is free (no collision)
- [ ] Never touches: `~/.ssh/`, `~/.gitconfig`, shell configs, `~/.profile`, system libraries

### 4.2 Execution Order

Always execute in this order within each category:

1. **Safest first**: empty dirs, caches, .DS_Store
2. **Moves**: reorganize files into proper directories
3. **Large deletes**: installers, regenerable dirs, orphaned tools
4. **Archives**: old projects (after git backup verification)

### 4.3 Git-Protected Archive Procedure

When archiving a project directory that is a git repo:

1. Check for unpushed commits: `git log @{u}..HEAD --oneline`
2. If unpushed commits exist, create and push a backup branch:
   ```bash
   git branch backup/pre-archive-$(date +%Y%m%d)
   git push origin backup/pre-archive-$(date +%Y%m%d)
   ```
3. Check for untracked files: `git ls-files --others --exclude-standard`
4. Strip regenerable directories: `rm -rf node_modules .venv __pycache__`
5. Move to archive directory

### 4.4 Safe Deletion Patterns

```bash
# Empty directory → safe to remove
rm -rf /path/to/empty-dir

# Installer packages — verify app installed first
test -d "/Applications/AppName.app" && rm -f /path/to/AppName.dmg

# Regenerable directories — always safe
rm -rf project/node_modules project/.venv project/__pycache__

# .DS_Store cleanup — safe everywhere
find ~ -name ".DS_Store" -not -path "*/Library/*" -delete
```

---

## Phase 5: VERIFY — Confirm Results

After execution, verify:

1. Re-measure: `du -sh ~/` and compare to baseline
2. List remaining items in affected directories to confirm moves
3. Report savings per category
4. Note anything that couldn't be completed (e.g., permission errors)

Present a clean before/after summary to the user.

---

## Bundled Scripts

These scripts handle deterministic, repeatable tasks. Use them instead of ad-hoc shell commands.

| Script | Purpose |
|---|---|
| `scripts/analyze_filesystem.py` | Recursive size map of any directory tree |
| `scripts/find_duplicates.py` | Checksum-based duplicate detection |
| `scripts/classify_dotfiles.py` | Cross-reference dotdirs against installed tools |
| `scripts/check_git_state.py` | Audit git repos for unpushed/dirty state |
| `scripts/clean_dsstore.py` | Safe .DS_Store removal with path exclusions |
| `scripts/strip_regenerable.py` | Identify and optionally remove node_modules, venvs, caches |

## References

| File | When to Read |
|---|---|
| `references/categorization_guide.md` | During Phase 2 — helps classify findings correctly |
| `references/safety_rules.md` | Before Phase 4 — mandatory safety checklist |
