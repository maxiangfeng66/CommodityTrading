# Architecture Guide for Claude

This document helps Claude understand the codebase structure and avoid creating duplicate code.

## Housekeeper System

A semantic housekeeper automatically runs on every conversation start and before every file write.

**How it works:**
1. On conversation start: Rebuilds function/class index
2. Before writing .py files: Checks for similar existing code
3. If duplicate found: BLOCKS and tells Claude to modify existing code instead

**Location:** `scripts/housekeeper/`

## Project Structure

```
CommodityTrading/
├── brain/                     # Core design documents
│   ├── blueprint.md           # Architecture documentation
│   └── Idea.txt               # Vision document
├── agents/                    # All agent classes
│   ├── core/                  # Core modules
│   │   ├── data_fetch.py      # Data fetching
│   │   └── debate.py          # Debate protocol
│   ├── level1/                # Strategic agents (PM, SUP, APPROVAL)
│   ├── level2/                # Tactical agents (Task Managers)
│   └── support/               # Support agents (Housekeeper)
├── modules/                   # Module outputs per commodity
├── output/                    # Final deliverables (HTML reports)
├── docs/                      # GitHub Pages
├── data/                      # Data storage
│   ├── raw/                   # Unprocessed data
│   ├── processed/             # Cleaned data
│   └── cache/                 # Temporary cache
├── archive/                   # Archived sessions
├── temp/                      # Temporary files
├── scripts/                   # CLI scripts
│   └── housekeeper/           # Code duplication checker
├── run.py                     # Main entry point
├── tidyup.md                  # Cleanup rules
└── CLAUDE.md                  # This file
```

## Rules for New Code

### Creating New Agents
- Place agent files in `agents/` and appropriate subdirectory
- Level 1 (Strategic): `agents/level1/`
- Level 2 (Tactical): `agents/level2/`
- Support agents: `agents/support/`

### Creating New Functions
- First check if similar function exists (housekeeper will catch this)
- If extending functionality, modify the existing function
- Core utilities go in `agents/core/`

### Creating New Classes
- Check for existing similar classes first
- Task Managers go in `agents/level2/`
- Follow the existing TM pattern (TM-FUND, TM-NEWS, etc.)

### File Management
- Follow `tidyup.md` rules for file lifecycle
- Permanent files: brain/, tidyup.md, output/*.html
- Session files: log.md, modules/*, data/processed/
- Temporary files: data/cache/*, temp/*

## Known Duplications to Avoid

| Don't Create | Use Instead | Location |
|--------------|-------------|----------|
| New entry point | Existing run.py | `run.py` |
| Duplicate TM class | Existing TM classes | `agents/level2/` |
| New debate system | Existing debate.py | `agents/core/debate.py` |

## Entry Points

- `run.py` - Primary entry point for all workflows
- Avoid creating new `run_*.py` files

## File Location Rules

| Type | Allowed Locations |
|------|-------------------|
| Agent classes | `agents/` and subdirectories |
| Core utilities | `agents/core/` |
| Level 1 agents | `agents/level1/` |
| Level 2 agents | `agents/level2/` |
| Support agents | `agents/support/` |
| Scripts | `scripts/` |

## Hard Rules (from blueprint.md)

1. **Folder Management** - Follow tidyup.md rules
2. **Blueprint Discipline** - Keep brain/blueprint.md concise and accurate
3. **Report Consistency** - Template/layout must NOT change between reruns
4. **User Approval Gate** - Show plan and ask user approval before execution

## Cleanup Rules

See `tidyup.md` for detailed cleanup rules including:
- Safe to delete: temp/*, data/cache/*
- Archive after session: log.md, modules/*
- Never delete: brain/*, tidyup.md, output/*.html
