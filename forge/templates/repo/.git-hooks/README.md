# Git Hooks for WorkshopForge Workshops

This directory contains git hooks that support AI-assisted workshop development.

## Available Hooks

### `prepare-commit-msg`

Reminds AI assistants to update `.claude/context.md` before committing changes.

**Why?**
- Maintains session continuity across AI sessions
- Ensures context.md reflects current workshop state
- Prevents stale information in future sessions

**What it does:**
- Checks if `.claude/context.md` was modified in the commit
- If not, adds reminder comment to commit message
- Suggests how to update and amend the commit

## Installation

These hooks are automatically installed when you initialize a git repository in this workshop.

**Manual installation:**
```bash
# From workshop root
cp .git-hooks/prepare-commit-msg .git/hooks/
chmod +x .git/hooks/prepare-commit-msg
```

## Usage

The hooks run automatically during git operations. No action required.

If you see a reminder in your commit message:

1. Edit `.claude/context.md` with current status
2. Stage the change: `git add .claude/context.md`
3. Amend the commit: `git commit --amend`

## Disabling

To temporarily disable a hook:
```bash
# Rename the hook
mv .git/hooks/prepare-commit-msg .git/hooks/prepare-commit-msg.disabled
```

To permanently disable:
```bash
# Delete the hook
rm .git/hooks/prepare-commit-msg
```

---

**Part of WorkshopForge** - https://github.com/cdds-ab/workshopforge
