# CommodityTrading Multi-Agent System Blueprint

## Core Vision
A self-supervising multi-agent system that produces comprehensive commodity analysis reports (HTML with visuals) combining **Fundamentals Outlook** and **Technical Analysis**, with quality ensured through hierarchical debate.

---

## System Flowchart

```
                                         USER REQUEST
                                              |
                              [Understand, Think, Plan]
                                              |
                                              v
+=======================================================================================+
|                              LEVEL 1: STRATEGIC LAYER                                  |
+=======================================================================================+
|                                                                                        |
|    +--------+          +---------+          +------------+                             |
|    |   PM   |--------->|   SUP   |--------->|  APPROVAL  |                             |
|    | Design |  review  |Challenge|  verify  |  Evaluate  |                             |
|    +--------+          +---------+          +------------+                             |
|         |                                         |                                    |
|         |  [If APPROVED]                          | [Verify vs BigIdea/Principles]     |
|         v                                         v                                    |
|    Allocate tasks                          APPROVED / REJECT                           |
|                                                                                        |
+=======================================================================================+
                                              |
                                              | APPROVED
                                              v
+=======================================================================================+
|                         USER APPROVAL GATE (Hard Rule #6)                              |
+=======================================================================================+
|   Show: Flowchart + Detailed Plan  -->  ASK USER: "Approve to proceed?"                |
+=======================================================================================+
                                              |
                                              | USER APPROVED
                                              v
+=======================================================================================+
|                         LEVEL 2: TACTICAL LAYER (PARALLEL)                             |
+=======================================================================================+
|                                                                                        |
|  +-------------+  +-------------+  +-------------+  +-------------+                    |
|  |  TM-FUND    |  |  TM-NEWS    |  |  TM-VIEWS   |  |  TM-TECH    |                    |
|  | Fundamentals|  | News/Policy |  | Market Views|  | Technical   |                    |
|  +------+------+  +------+------+  +------+------+  +------+------+                    |
|         |                |                |                |                           |
|  +------+------+  +------+------+  +------+------+  +------+------+                    |
|  |SUP-A | SUP-B|  |SUP-A | SUP-B|  |SUP-A | SUP-B|  |SUP-A | SUP-B|                    |
|  +-------------+  +-------------+  +-------------+  +-------------+                    |
|                                                                                        |
|  +-------------+  +-------------+                                                      |
|  |  TM-STRUCT  |  |  TM-POS     |     [Each module: min 2 debate rounds]               |
|  | Mkt Structure|  | Positioning |                                                      |
|  +------+------+  +------+------+                                                      |
|         |                |                                                             |
|  +------+------+  +------+------+                                                      |
|  |SUP-A | SUP-B|  |SUP-A | SUP-B|                                                      |
|  +-------------+  +-------------+                                                      |
|                                                                                        |
+=======================================================================================+
                                              |
                                              | ALL MODULES COMPLETE
                                              v
+=======================================================================================+
|                              TM-REPORT: SYNTHESIS                                      |
+=======================================================================================+
|   Inputs: 6x output.json + debate logs  -->  Output: output/[commodity].html           |
+=======================================================================================+
                                              |
                                              v
+=======================================================================================+
|                              FINAL REVIEW                                              |
+=======================================================================================+
|                    SUP + APPROVAL --> Verify complete report                           |
+=======================================================================================+
                                              |
                                              v
+=======================================================================================+
|                              HOUSEKEEPING                                              |
+=======================================================================================+
|                    HOUSEKEEPER agent enforces tidyup.md rules                          |
+=======================================================================================+
                                              |
                                              v
                                     DELIVERABLES:
                                     - output/[commodity].html
                                     - Control Room (workflow monitor)
```

---

## Principles

| Principle | Implementation |
|-----------|----------------|
| **Think Before Execute** | Understand, think, plan before any execution |
| **Maximize Parallelism** | Level 2 modules 1-6 execute concurrently |
| **Efficiency** | Carefully designed agent system, balance quality vs cost |
| **Modularity** | Each module independent, easily modified/replaced |
| **Repeatability** | Same standard/layout for any commodity, daily updatable |
| **Quality via Debate** | Every task manager challenged by 2 supervisors |

---

## Architecture

### Level 1: Strategic Agents

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **PM** | Project Manager | Design plan, allocate tasks, coordinate Level 2 |
| **SUP** | Supervisor | Challenge PM step-by-step, validate logic |
| **APPROVAL** | Evaluator | Verify design matches BigIdea/Principles/Architect, approve/reject |

### Level 2: Tactical Agents

Each Task Manager (TM) has **2 supervising agents** for debate:
- **SUP-A**: Logic Challenger (questions assumptions, reasoning)
- **SUP-B**: Data Validator (verifies data sources, calculations)

| Task Manager | Scope | Key Metrics |
|--------------|-------|-------------|
| **TM-FUND** | Supply/demand balance, production, seasonal | Stocks-to-use, surplus/deficit |
| **TM-NEWS** | Policy, weather, recent developments | Impact severity (1-5) |
| **TM-VIEWS** | Market consensus, logic soundness | Bullish/bearish sentiment |
| **TM-TECH** | Trend (60MA), momentum, key levels | Price vs MA, RSI, triggers |
| **TM-STRUCT** | Volume, OI, crowding | 5-day avg, OI percentile |
| **TM-POS** | COT, CTA positioning | Net position percentile |
| **TM-REPORT** | HTML synthesis, visualizations | Template consistency |

### Support Agents

| Agent | Role | Trigger |
|-------|------|---------|
| **HOUSEKEEPER** | Enforce tidyup.md rules | After each run |

---

## Hybrid Agent Architecture

The system uses a **hybrid approach** combining code-based agents (permanent infrastructure) with LLM agents (temporary workers for reasoning tasks).

### Agent Types

| Type | Lifespan | Strength | Best For |
|------|----------|----------|----------|
| **Code-Based** | Permanent | Structured, predictable, cheap | Orchestration, data fetch, formatting |
| **LLM Workers** | Temporary | Reasoning, synthesis, creative | Analysis, debate, insights |

### Division of Labor

| Task | Agent Type | Rationale |
|------|-----------|-----------|
| Fetch price data from Yahoo | **Code** | API call, no reasoning needed |
| Parse COT report | **Code** | Structured data extraction |
| Interpret what COT data means | **LLM** | Requires market knowledge |
| Calculate 60-day MA | **Code** | Math, deterministic |
| Decide if trend is bullish/bearish | **LLM** | Interpretation, context |
| Challenge analysis logic | **LLM** | Reasoning, debate |
| Generate HTML report | **Code** | Template-based |
| Write executive summary | **LLM** | Synthesis, narrative |

### Spawning Pattern

```
Code-Based TM (permanent)
    │
    ├── 1. CODE: Fetch data (cheap, fast)
    ├── 2. CODE: Pre-process (deterministic)
    ├── 3. LLM: Spawn data_interpreter (temporary)
    ├── 4. LLM: Spawn sup_a_challenger (debate)
    ├── 5. LLM: Spawn sup_b_validator (debate)
    └── 6. CODE: Format output (deterministic)
```

### LLM Worker Roles

| Role | Icon | Task |
|------|------|------|
| `data_interpreter` | 🔍 | Interpret raw data into insights |
| `trend_analyzer` | 📊 | Identify patterns and trends |
| `sentiment_scorer` | 💬 | Score news/views sentiment |
| `logic_challenger` | ⚔️ | Challenge reasoning (SUP-A) |
| `data_validator` | ✅ | Validate data accuracy (SUP-B) |
| `insight_synthesizer` | ✍️ | Generate final insights |

### Cost Optimization

| Model | Use For |
|-------|---------|
| **Haiku** (cheap) | Data interpretation, simple validation |
| **Sonnet** (balanced) | Analysis, debate rounds |
| **Opus** (powerful) | Executive summaries, complex synthesis |

---

## Deliverables

| Deliverable | Location | Purpose |
|-------------|----------|---------|
| **Commodity Report** | `output/[commodity].html` | Final analysis with visuals |
| **Control Room** | `output/control_room.html` | Workflow monitor for approval/tracking |
| **Tidyup Executable** | `tidyup.bat` / `tidyup.sh` | Manual cleanup trigger |

---

## Debate Protocol

```
Round 1:
  TM --> Initial Analysis
  SUP-A --> Challenge logic/assumptions
  TM --> Respond with clarifications
  SUP-B --> Validate data/methodology

Round 2+:
  TM --> Revised analysis
  SUP-A --> Final logic check
  SUP-B --> Final data validation
  --> Outcome: Accept / Revise / Escalate

Escalation: If unresolved after 3 rounds --> Level 1 SUP
```

---

## Output Structure (HTML Report - Fixed Template)

```
1. Executive Summary (Outlook, Key Drivers, Risks)
2. Fundamentals (Supply/Demand, Balance Chart)
3. News & Policy (Timeline, Impact Assessment)
4. Market Views (Consensus, Logic Assessment)
5. Technical (Trend Charts, Key Levels, MA Analysis)
   - MUST include: Interactive price candlestick chart
6. Market Structure (Volume/OI, Attention Metrics)
7. Positioning (COT Charts, Crowding Metrics)
8. Conclusion (Synthesis, Trading Implications, Confidence)
```

### Report Content Requirements
- **Interactive candlestick chart** in Technical section (required)
- **Detailed bullet points** - not just keywords and scores
- Each section must provide specific details, rationale, and data points
- Visual supports where applicable

---

## Hard Rules (Military Policy Enforcement)

| # | Rule | Enforcement |
|---|------|-------------|
| 1 | **Folder Management** | Follow tidyup.md. HOUSEKEEPER agent enforces at each run |
| 2 | **Flowchart Validation** | SUP + APPROVAL verify flowchart matches BigIdea/Principles/Architect |
| 3 | **Blueprint Versioning** | Log flowchart changes here with version history for rollback |
| 4 | **Blueprint Discipline** | This file: brain/blueprint.md. Concise, accurate, up-to-date. NOT a log |
| 5 | **Report Consistency** | Template/layout must NOT change between reruns |
| 6 | **User Approval Gate** | Before execution: show flowchart + detailed plan, ask user approval to proceed |
| 7 | **No Code Duplication** | Claude Code hooks BLOCK duplicate functions/classes. Modify existing code instead |

---

## Code Duplication Prevention (Hard Rule #7)

A semantic housekeeper system automatically prevents code duplication via Claude Code hooks.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
├─────────────────────────────────────────────────────────────┤
│  1. Claude attempts to Write/Edit a .py file                │
│                         ↓                                    │
│  2. PreToolUse Hook triggers: scripts/housekeeper/main.py   │
│                         ↓                                    │
│  3. Housekeeper checks:                                      │
│     - Exact function/class name match?                       │
│     - Semantic similarity via embeddings?                    │
│     - Blocked filename pattern (run_*.py, main*.py)?        │
│                         ↓                                    │
│  4. If duplicate found → EXIT CODE 2 → BLOCK WRITE          │
│     If unique code    → EXIT CODE 0 → ALLOW WRITE           │
│                         ↓                                    │
│  5. PostToolUse Hook: Rebuild index after successful write  │
└─────────────────────────────────────────────────────────────┘
```

### Configuration Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Hook configuration (PreToolUse, PostToolUse) |
| `.claude/function_index.json` | Index of all functions/classes with embeddings |
| `scripts/housekeeper/` | Housekeeper scripts (main.py, indexer.py, etc.) |
| `CLAUDE.md` | Architecture guide for Claude |

### What Gets Blocked

1. **Exact name duplicates**: Function/class with same name as existing
2. **Semantic duplicates**: Code that does the same thing (detected via embeddings)
3. **New entry points**: Files matching `run_*.py`, `main*.py`, `app*.py` at project root

### Allowed Entry Points

Only `run.py` is permitted as an entry point. All other entry-point patterns are blocked.

### Override Mechanism

Add `# HOUSEKEEPER_OVERRIDE: <reason>` in the file to bypass checks (use sparingly).

### Maintenance

- Index auto-rebuilds after each file write
- Manual rebuild: `python scripts/housekeeper/indexer.py --rebuild`
- Requires: `pip install sentence-transformers numpy`

---

## Real-Time Visualizer

A web-based visualizer shows live progress of commodity analysis.

### How to Start

```bash
# Method 1: Direct start
python visualizer/serve_visualizer.py

# Method 2: Windows batch file
visualizer\Run Visualizer.bat
```

Opens browser at `http://localhost:8765`

### Components

| File | Purpose |
|------|---------|
| `visualizer/visualizer_bridge.py` | State management (singleton) |
| `visualizer/serve_visualizer.py` | HTTP server with API endpoints |
| `visualizer/commodity_trading.html` | Frontend UI (retro arcade theme) |
| `context/visualizer_state.json` | Current analysis state (auto-generated) |

### API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /` | Frontend HTML page |
| `GET /api/state` | Current visualizer state JSON |
| `GET /api/outputs` | Module outputs by commodity |

### Integration with Agents

```python
from visualizer import get_visualizer

# Get singleton bridge
bridge = get_visualizer()

# Lifecycle
bridge.start_analysis("Cotton", "ICE Cotton #2")
bridge.complete_analysis()

# Agent updates
bridge.agent_start("tm_fund", "Fetching data", tier=2)
bridge.agent_progress("tm_fund", "Processing...")
bridge.agent_complete("tm_fund")

# Module tracking
bridge.module_start("tm_tech", "Technical analysis")
bridge.module_complete("tm_tech", score=2.5)

# Debate tracking
bridge.debate_start("tm_fund", round_num=1)
bridge.debate_complete("tm_fund", "ACCEPTED", rounds=3)

# Dynamic agent spawning
bridge.spawn_agent("research_1", parent_id="PM", role="Research", task="Fetching data")
bridge.agent_progress("research_1", "Processing...")
bridge.agent_complete("research_1")
bridge.terminate_agent("research_1", "Data collected")
```

### Dynamic Agent Spawning

When agents spawn sub-agents at runtime, the visualizer automatically creates visual nodes:

- **Spawned Agents Section**: Appears below the main flowchart when sub-agents exist
- **Parent Tracking**: Shows `↳ parent_name` under each spawned agent
- **Role-based Icons**: Research (🔍), Analysis (📊), Validator (✅), Debate (⚔️)
- **Auto-cleanup**: Nodes disappear when agents are terminated

### Display Features

- Real-time progress bar
- Agent status indicators (idle/thinking/complete/error)
- Chat log with timestamped entries
- Module scores visualization
- Click agent nodes to view output details
- **Dynamic spawned agents** with parent relationships

---

## Execution Flow

```
1. UNDERSTAND  : Read commodity list, gather context
2. THINK       : PM designs analysis plan
3. PLAN        : SUP challenges, APPROVAL verifies vs blueprint
4. SHOW & ASK  : Display flowchart + detailed plan, ASK USER APPROVAL (Hard Rule #6)
5. EXECUTE     : Level 2 modules run in parallel with debates
6. SYNTHESIZE  : TM-REPORT compiles HTML report (with candlestick chart)
7. REVIEW      : SUP + APPROVAL evaluate complete report
8. DELIVER     : HTML report to output/
9. CLEANUP     : HOUSEKEEPER enforces tidyup.md
```

---

## Folder Structure

```
CommodityTrading/
├── .claude/              # Claude Code configuration (Hard Rule #7)
│   ├── settings.json     # Hook configuration (PreToolUse, PostToolUse)
│   └── function_index.json # Auto-generated function/class index
├── brain/
│   ├── blueprint.md      # This file (architecture)
│   └── Idea.txt          # Vision document (source of truth)
├── agents/               # Code-based agent system
│   ├── core/             # Core modules
│   │   ├── data_fetch.py # Data fetching from public sources
│   │   └── debate.py     # Debate protocol engine
│   ├── level1/           # Strategic agents
│   │   ├── pm.py         # Project Manager
│   │   ├── sup.py        # Supervisor
│   │   └── approval.py   # Approval Agent
│   ├── level2/           # Tactical agents (Task Managers)
│   │   ├── base.py       # Base TM class
│   │   ├── tm_fund.py    # Fundamentals
│   │   ├── tm_news.py    # News & Policy
│   │   ├── tm_views.py   # Market Views
│   │   ├── tm_tech.py    # Technical Analysis
│   │   ├── tm_struct.py  # Market Structure
│   │   ├── tm_pos.py     # Positioning
│   │   └── tm_report.py  # HTML Synthesis
│   └── support/
│       └── housekeeper.py # Cleanup agent
├── scripts/              # CLI scripts
│   └── housekeeper/      # Code duplication prevention (Hard Rule #7)
│       ├── main.py       # Hook entry point
│       ├── indexer.py    # Code indexing
│       ├── similarity.py # Similarity detection
│       ├── embedder.py   # Embedding generation
│       ├── llm_checker.py # Semantic checking
│       └── config.py     # Configuration
├── visualizer/           # Real-time visualization
│   ├── visualizer_bridge.py  # State management
│   ├── serve_visualizer.py   # HTTP server
│   ├── commodity_trading.html # Frontend UI
│   └── Run Visualizer.bat    # Quick start (Windows)
├── context/              # Runtime state
│   └── visualizer_state.json # Auto-generated
├── modules/
│   └── [commodity]/      # Per-commodity outputs
├── output/
│   ├── [commodity].html  # Final reports
│   └── control_room.html # Workflow monitor
├── docs/                 # GitHub Pages (mirror of output/)
├── data/
│   ├── raw/              # Unprocessed fetched data
│   ├── processed/        # Cleaned/transformed data
│   └── cache/            # Temporary cache (auto-cleaned)
├── archive/              # Archived sessions by date
├── temp/                 # Temporary files (auto-cleaned)
├── run.py                # Main entry point (ONLY allowed entry point)
├── CLAUDE.md             # Architecture guide for Claude
├── log.md                # Session logs
├── tidyup.md             # Cleanup rules
├── tidyup.bat            # Manual cleanup (Windows)
└── tidyup.sh             # Manual cleanup (Unix)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-20 | Initial architecture (Cotton-focused) |
| 2.0 | 2026-01-22 | Generalized framework: APPROVAL agent, Hard Rules, Principles |
| 2.1 | 2026-01-22 | Added Hard Rule: Report Consistency |
| 2.2 | 2026-01-22 | Added HOUSEKEEPER agent, Control Room, "Think Before Execute", Efficiency principle, tidyup executables |
| 2.3 | 2026-01-22 | Project restructure: Created data/, archive/, temp/ folders. Added docs/ for GitHub Pages. Archived legacy module structure |
| 3.0 | 2026-01-22 | Code-based agent system implemented. All agents operational. Tested with Aluminum. |
| 3.1 | 2026-01-22 | Per Idea.txt: Added Hard Rule #6 (User Approval Gate - show flowchart/plan, ask approval). Added report requirements: interactive candlestick chart, detailed bullet points. "Military Policy" enforcement. Execution flow now 9 steps. |
| 3.2 | 2026-01-28 | Added Hard Rule #7 (No Code Duplication). Implemented Claude Code hooks via `.claude/settings.json` and `scripts/housekeeper/`. Semantic housekeeper blocks duplicate functions/classes using embeddings. Added CLAUDE.md. |
| 3.3 | 2026-01-28 | Added real-time visualizer (equity-minions style). HTTP server with polling at `localhost:8765`. Retro arcade UI showing agent progress, module scores, debate rounds. Created `visualizer/` and `context/` directories. |
| 3.4 | 2026-01-28 | Enhanced visualizer with dynamic agent spawning. Agents can spawn sub-agents at runtime with `spawn_agent()` and `terminate_agent()`. Frontend auto-creates/removes visual nodes. Shows parent relationships and role-based icons. |
| 3.5 | 2026-01-28 | Documented hybrid agent architecture. Code-based agents (permanent) orchestrate LLM workers (temporary) for reasoning tasks. Division of labor: code for data/formatting, LLM for analysis/debate/synthesis. Cost optimization with Haiku/Sonnet/Opus tiers. |
