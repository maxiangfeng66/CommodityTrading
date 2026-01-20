# Folder Management & Cleanup Rules

## Directory Structure

```
CommodityTrading/
├── blueprint.md          # Architecture documentation (KEEP)
├── log.md               # Session logs (KEEP)
├── tidyup.md            # This file (KEEP)
├── design.txt           # Original requirements (KEEP)
│
├── data/                # Raw data storage
│   ├── raw/            # Unprocessed fetched data
│   ├── processed/      # Cleaned/transformed data
│   └── cache/          # Temporary cache files
│
├── modules/             # Module outputs
│   ├── fundamentals/
│   ├── news/
│   ├── market_views/
│   ├── technical/
│   ├── structure/
│   ├── positioning/
│   └── report/
│
├── output/              # Final deliverables
│   ├── report.html     # Main deliverable
│   ├── charts/         # Generated visualizations
│   └── assets/         # CSS, JS, images
│
├── archive/             # Archived sessions
│   └── YYYY-MM-DD/     # Date-organized archives
│
└── temp/               # Temporary working files
```

---

## File Lifecycle Rules

### Permanent Files (Never Delete)
- `blueprint.md` - Core architecture
- `design.txt` - Original requirements
- `tidyup.md` - This rulebook
- `output/report.html` - Final deliverable (latest version)

### Session Files (Archive after session)
- `log.md` - Move to archive after session complete
- `modules/*/` - Archive after report generated
- `data/processed/` - Archive with session

### Temporary Files (Delete after use)
- `data/cache/*` - Delete after 24 hours
- `temp/*` - Delete after session
- `data/raw/*` - Delete after processing complete

---

## Archive Rules

### When to Archive
1. Session complete and report delivered
2. Starting new analysis on same commodity
3. Weekly cleanup (every Sunday)

### Archive Process
```
1. Create folder: archive/YYYY-MM-DD/
2. Move: log.md → archive/YYYY-MM-DD/log.md
3. Move: modules/* → archive/YYYY-MM-DD/modules/
4. Move: data/processed/* → archive/YYYY-MM-DD/data/
5. Keep: output/report.html (rename with date if new report)
6. Delete: temp/*, data/cache/*
```

### Archive Naming Convention
- Folders: `YYYY-MM-DD` (date of archive)
- Reports: `report_YYYYMMDD_HHMM.html` (datetime of generation)

---

## Deletion Rules

### Safe to Delete (No confirmation needed)
- Files in `temp/`
- Files in `data/cache/` older than 24h
- Empty directories
- `.tmp`, `.bak` files

### Require Confirmation Before Delete
- Any file in `output/`
- Any file in `modules/` not yet archived
- `log.md` before archiving
- Any `.md` file not in archive/

### Never Delete Automatically
- `blueprint.md`
- `design.txt`
- `tidyup.md`
- Files in `archive/`

---

## Cleanup Commands

### Daily Cleanup
```
Delete: temp/*
Delete: data/cache/* (>24h old)
```

### Session End Cleanup
```
Archive: Current session files
Delete: temp/*
Delete: data/cache/*
Delete: data/raw/* (if processed)
```

### Full Archive
```
Archive: All session data
Keep: Core documentation
Keep: Latest report
Delete: All temp/cache
```

---

## File Size Limits

| Directory | Max Size | Action if Exceeded |
|-----------|----------|-------------------|
| data/cache | 100MB | Delete oldest files |
| data/raw | 50MB | Process and delete |
| temp | 20MB | Immediate cleanup |
| archive | 500MB | Compress old archives |

---

## Module Output Standards

Each module must produce:
```
modules/[module_name]/
├── output.json          # Structured data output
├── summary.md           # Human-readable summary
├── debate_log.md        # Debate round records
└── sources.md           # Data source citations
```

---

## Version Control

### Files to Commit
- All `.md` files
- `output/report.html`
- `modules/*/output.json`

### Files to .gitignore
```
temp/
data/cache/
data/raw/
*.tmp
*.bak
*.log
```

---

## Maintenance Schedule

| Task | Frequency | Automated |
|------|-----------|-----------|
| Cache cleanup | Daily | Yes |
| Temp cleanup | Per session | Yes |
| Archive check | Weekly | No |
| Full archive | Monthly | No |
| Size audit | Monthly | No |
