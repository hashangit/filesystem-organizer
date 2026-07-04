# 🗂️ Filesystem Organizer

<p align="center">
  <em>A systematic, safety-first toolkit for auditing, cleaning, and organizing your filesystem — <strong>without data loss</strong>.</em>
</p>

<p align="center">
  <a href="#-quick-start"><strong>Quick Start</strong></a> ·
  <a href="#-what-it-does"><strong>What It Does</strong></a> ·
  <a href="#-toolkit"><strong>Toolkit</strong></a> ·
  <a href="#-methodology"><strong>Methodology</strong></a> ·
  <a href="#-safety"><strong>Safety</strong></a> ·
  <a href="#-installation"><strong>Installation</strong></a> ·
  <a href="#-contributing"><strong>Contributing</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
  <img src="https://img.shields.io/badge/safety-dry--run--by--default-brightgreen" alt="Safety First">
</p>

---

## 🎯 What It Does

**Filesystem Organizer** turns a messy, bloated home directory into a clean, navigable workspace. It doesn't just delete files — it audits, categorizes, and presents a plan. You decide what stays and what goes.

### What a typical cleanup uncovers

| Finding | Impact | Solution |
|---|---|---|
| Orphaned tool configs | Dotdirs for uninstalled CLIs and apps | Identified via cross-reference, removed |
| Regenerable bloat | `node_modules/`, `.venv/`, caches weighing down projects | Stripped before archiving |
| Duplicate files | Identical content under different names | Checksum detection, keep best copy |
| Stale project iterations | Renamed/evolved repos left behind | Git backup → archive |
| Misplaced files | Documents in downloads, configs at filesystem root | Filed into proper structure |
| Old app installers | Disk images and packages after app installed | Safely deleted |
| Empty directories | Abandoned scaffolds and zero-byte artifacts | Removed |

---

## 🚀 Quick Start

```bash
# Clone the toolkit
git clone https://github.com/hashangit/filesystem-organizer.git
cd filesystem-organizer

# Map your filesystem — find what's eating your disk
python scripts/analyze_filesystem.py ~/projects ~/documents ~/downloads

# Find dotfiles for uninstalled tools
python scripts/classify_dotfiles.py

# Find duplicate files
python scripts/find_duplicates.py ~/documents ~/downloads --min-size 1MB

# Check git repos for unpushed work before archiving
python scripts/check_git_state.py ~/projects

# Find regenerable bloat (node_modules, venvs, caches)
python scripts/strip_regenerable.py ~/projects

# Count .DS_Store files (macOS)
python scripts/clean_dsstore.py ~/

# All scripts default to DRY RUN. Add --execute to actually modify anything.
```

---

## 🧰 Toolkit

| Script | Purpose | Modifies? |
|---|---|---|
| `analyze_filesystem.py` | Recursive size map — find what's eating your disk | Read-only |
| `find_duplicates.py` | Checksum-based duplicate detection | Read-only |
| `classify_dotfiles.py` | Cross-reference `~/.dotdirs` against installed tools | Read-only |
| `check_git_state.py` | Audit git repos: unpushed commits, dirty state, untracked files | Read-only |
| `clean_dsstore.py` | Find and remove `.DS_Store` files | `--execute` required |
| `strip_regenerable.py` | Find and remove `node_modules/`, `.venv/`, caches | `--execute` required |

### Output Examples

**`analyze_filesystem.py`** — Where did my disk space go?
```
      SIZE  TYPE        PATH
--------------------------------------------------------------------------------
    1.8 GB  directory   /home/user/projects/web-app
  469.0 MB  directory   /home/user/projects/archived-lib
  247.3 MB  file        /home/user/downloads/AppInstaller.dmg
    1.2 GB  file        /home/user/.cache/large-index.json
```

**`classify_dotfiles.py`** — Which dotdirs can I safely delete?
```
DOTFILE CLASSIFICATION
============================================================
  Active:     24 — tool is installed
  Orphaned:   5  — tool NOT installed
  System:     15 — critical, never remove
  Unknown:    3  — investigate manually

ORPHANED — safe to remove
  .old-cli-tool                 Tool 'old-cli' is not installed
  .legacy-editor                Tool 'legacy-editor' is not installed
  .unused-agent                 Tool 'unused-agent' is not installed
```

**`check_git_state.py`** — Any unpushed work before archiving?
```
GIT REPOSITORY AUDIT — 12 repos found
============================================================
  NEEDS ATTENTION (2):
  📁 archived-service
     ⚠️  53 unpushed commits
     📝 12 uncommitted changes
  📁 prototype-lib
     ⚠️  5 unpushed commits
```

---

## 📋 Methodology

The skill follows a five-phase process:

```
Phase 1: DISCOVER  → Map everything, measure sizes, find issues
Phase 2: ANALYZE   → Categorize findings, estimate savings, present plan
Phase 3: CONFIRM   → User reviews and approves the plan
Phase 4: EXECUTE   → Carry out approved changes with safety checks
Phase 5: VERIFY    → Confirm results, report savings
```

### Built to Adapt

The bundled scripts are starting points — not finished products. The skill instructs the agent to **inspect and adapt every script to your system** before running:

- **`KNOWN_DOTDIRS` mapping** is extended on-the-fly as new tools are discovered on your machine
- **Paths and package managers** are adjusted to match your OS and setup (macOS, Linux, Homebrew, apt, npm, pnpm, etc.)
- **User directives** are codified into scripts immediately — if you say "never touch X," it becomes a rule

This means the toolkit gets smarter and more personalized with each use.

### What gets cleaned

| Category | Examples | Risk |
|---|---|---|
| **Empty artifacts** | Empty dirs, zero-byte files | None |
| **Regenerable cruft** | `node_modules/`, `.venv/`, caches | None |
| **Stale backups** | `.bak`, `.save` files with live version | Very low |
| **Orphaned tool data** | Dotdirs for uninstalled CLIs | Low |
| **Old app versions** | Previous IDE installs, old extensions | Low |
| **Duplicate files** | Checksum-identical copies | Medium |
| **Project iterations** | Renamed/evolved project dirs | Medium |

### Proposed directory structures

A clean home directory follows simple patterns. Adapt these to your own needs:

```
~/projects/                       ~/documents/
├── active-app/                   ├── personal/
├── open-source-lib/              │   ├── resumes/
├── secrets/    (API keys, envs)  │   ├── finance/
├── _backups/   (design snapshots)│   └── legal/
└── _archive/   (old projects)    ├── work/
                                  │   ├── client-a/
~/downloads/                      │   └── freelance/
Rule: if >2 weeks old,            ├── projects/
file it or delete it.             ├── secrets/
                                  └── archive/
```

---

## 🛡️ Safety — Non-Negotiable

> **This toolkit will never delete, move, or modify anything without your explicit, item-by-item approval.**

There is no "clean up everything" mode. There are no automatic deletions. Every destructive action requires you to review and approve it first.

1. **All destructive scripts default to dry-run.** They report what they *would* do. The `--execute` flag is gated behind user approval.
2. **Critical path protection.** Never touches `~/.ssh`, `~/.gitconfig`, shell configs, `~/.profile`, system libraries — these paths are hard-blocked.
3. **Git backup before archiving.** Repos with unpushed work get a `backup/pre-archive-YYYYMMDD` branch pushed to remote before any local changes.
4. **Four risk levels** with required confirmation for each. Medium and high-risk items require individual approval.
5. **Agent skill directive**: The SKILL.md enforces a non-negotiable "ask before destroy" clause at the very top — agents using this skill cannot bypass it.
6. **Read the full safety rules:** [`references/safety_rules.md`](references/safety_rules.md)


## 📦 Installation

### As a standalone toolkit
```bash
git clone https://github.com/hashangit/filesystem-organizer.git
cd filesystem-organizer
# All scripts are standalone Python with zero dependencies beyond stdlib
python scripts/analyze_filesystem.py ~/
```

### As an Agent Skill
Copy the directory to your agent's skills directory (path varies by agent):
```bash
cp -r filesystem-organizer /path/to/your/agent/skills/
```

The `SKILL.md` entry point triggers when the user mentions organizing files, cleaning up disk space, auditing their system, or decluttering.

### Requirements
- **Python 3.10+** (stdlib only — no pip install needed)
- **macOS or Linux** (some path patterns are Unix-specific)
- **Git** (for `check_git_state.py` and archive workflows)

---

## 🤝 Contributing

Contributions welcome! Areas that would benefit from community input:

- **Windows support** — path patterns and tool detection are currently Unix-focused
- **Additional package managers** — `classify_dotfiles.py` supports Homebrew and npm; PRs for `apt`, `pacman`, `choco`, `pipx` welcome
- **New dotdir mappings** — add entries to `KNOWN_DOTDIRS` in `classify_dotfiles.py`
- **More regenerable patterns** — extend `strip_regenerable.py` for other ecosystems (.NET, Go, Rust build artifacts)

### Development
```bash
git clone https://github.com/hashangit/filesystem-organizer.git
cd filesystem-organizer
python scripts/classify_dotfiles.py --json | python -m json.tool
```

---

## 📄 License

MIT © 2026 [Hashan Wickramasinghe](https://github.com/hashangit)

---

## ❤️ Support

If this toolkit saved you hours of cleanup or gigabytes of disk space, consider supporting its development:

<p align="center">
  <a href="https://www.paypal.com/ncp/payment/HR7GJ2RV7FFW6">
    <img src="https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal" alt="Donate with PayPal">
  </a>
</p>

---

<p align="center">
  <sub>Built with 🧹 by <a href="https://github.com/hashangit">Hashan Wickramasinghe</a></sub>
</p>
