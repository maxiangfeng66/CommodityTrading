"""
Housekeeper Configuration

Defines thresholds, paths, and settings for the semantic housekeeper.
"""

import os
from pathlib import Path

# Project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Similarity thresholds
NAME_SIMILARITY_THRESHOLD = 0.85      # For fuzzy name matching
EMBEDDING_SIMILARITY_THRESHOLD = 0.70  # Trigger LLM check above this
LLM_CONFIRMATION_THRESHOLD = 0.90      # Auto-block if LLM says >90% similar

# Paths
INDEX_PATH = PROJECT_ROOT / ".claude" / "function_index.json"
LOG_PATH = PROJECT_ROOT / ".claude" / "housekeeper.log"

# Directories to scan for functions/classes
SCAN_DIRS = [
    "agents",
    "scripts",
]

# Files/patterns to ignore
IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "test_*",
    "*_test.py",
    "conftest.py",
    ".git",
    ".venv",
    "venv",
    "node_modules",
]

# Specific files to ignore (won't be indexed or checked)
IGNORE_FILES = [
    "housekeeper",  # Don't index ourselves
]

# Blocked filename patterns - prevent creating new entry points
# These patterns match against the filename (not full path)
BLOCKED_FILENAME_PATTERNS = [
    "main*.py",      # main.py, main2.py, main_v2.py, etc.
    "run_*.py",      # run_workflow.py, run_tests.py, etc.
    "start_*.py",    # start_server.py, etc.
    "app*.py",       # app.py, application.py, etc.
    "server*.py",    # server.py, server_main.py, etc.
    "cli*.py",       # cli.py, cli_main.py, etc.
]

# Existing entry points that ARE allowed (whitelist)
ALLOWED_ENTRY_POINTS = [
    "run.py",                 # The main entry point
]

# Override marker - if this appears in file content, skip housekeeper checks
# Format: # HOUSEKEEPER_OVERRIDE: <reason>
OVERRIDE_MARKER = "HOUSEKEEPER_OVERRIDE:"

# File location rules: where different types of files should live
LOCATION_RULES = {
    "agent": ["agents/"],
    "provider": ["agents/"],
    "validator": ["agents/"],
    "util": ["agents/core/"],
    "tool": ["agents/tools/"],
}

# Import rules: deprecated modules and their replacements
DEPRECATED_IMPORTS = {
    # Add deprecated imports here as needed
}

# LLM prompt for semantic comparison
LLM_COMPARISON_PROMPT = """You are a code similarity analyzer. Compare these two code snippets and determine if they serve the same purpose.

Function A (NEW - about to be created):
```python
{new_code}
```

Function B (EXISTING - already in codebase):
```python
{existing_code}
```

Answer with ONLY one of these responses:
- "SAME" - if they do essentially the same thing (even with different names/implementation)
- "DIFFERENT" - if they serve different purposes
- "SIMILAR" - if they overlap but have distinct use cases

Then on a new line, briefly explain why (max 20 words).
"""

# System prompt for LLM
LLM_SYSTEM_PROMPT = """You are a precise code analyzer. Your job is to determine if two functions/classes serve the same purpose.
Be strict: if there's meaningful difference in what they do, say DIFFERENT.
Only say SAME if they are truly interchangeable."""
