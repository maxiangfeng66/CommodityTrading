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
├── run.py                # Main entry point
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
