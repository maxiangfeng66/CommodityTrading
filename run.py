#!/usr/bin/env python3
"""
CommodityTrading Multi-Agent Analysis System
Main entry point

Usage:
    python run.py aluminum
    python run.py --commodity aluminum
    python run.py --list   # Show available commodities
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Project root
PROJECT_ROOT = Path(__file__).parent

# Add agents to path
sys.path.insert(0, str(PROJECT_ROOT))

from agents.level1.pm import ProjectManager
from agents.level1.sup import Supervisor
from agents.level1.approval import ApprovalAgent
from agents.level2.tm_fund import FundamentalsManager
from agents.level2.tm_news import NewsManager
from agents.level2.tm_views import ViewsManager
from agents.level2.tm_tech import TechnicalManager
from agents.level2.tm_struct import StructureManager
from agents.level2.tm_pos import PositioningManager
from agents.level2.tm_report import ReportManager
from agents.support.housekeeper import Housekeeper


# Available commodities
COMMODITIES = [
    "aluminum",
    "copper",
    "cotton",
    "sugar",
    "silver",
    "iron_ore",
]


def log_event(log_path: Path, agent: str, action: str, status: str, notes: str = ""):
    """Append event to log.md"""
    timestamp = datetime.now().strftime("%H:%M")

    entry = f"\n### [{timestamp}] {action}\n"
    entry += f"- **Agent:** {agent}\n"
    entry += f"- **Action:** {action}\n"
    entry += f"- **Status:** {status}\n"
    if notes:
        entry += f"- **Notes:** {notes}\n"

    with open(log_path, 'a') as f:
        f.write(entry)


def run_analysis(commodity: str, parallel: bool = True, force_refresh: bool = False):
    """
    Run full analysis pipeline for a commodity.

    Execution Flow per Blueprint:
    1. UNDERSTAND - Read commodity, gather context
    2. THINK - PM designs analysis plan
    3. PLAN - SUP challenges, APPROVAL verifies
    4. EXECUTE - Level 2 modules run in parallel with debates
    5. SYNTHESIZE - TM-REPORT compiles HTML
    6. REVIEW - SUP + APPROVAL evaluate
    7. DELIVER - Output report
    8. CLEANUP - HOUSEKEEPER runs
    """
    print(f"\n{'='*60}")
    print(f"  COMMODITY ANALYSIS: {commodity.upper()}")
    if force_refresh:
        print(f"  MODE: FRESH DATA (bypassing cache)")
    print(f"{'='*60}\n")

    log_path = PROJECT_ROOT / "log.md"

    # Initialize session in log
    date_str = datetime.now().strftime("%Y-%m-%d")
    with open(log_path, 'a') as f:
        f.write(f"\n## Session: {date_str}\n")

    # =========================================
    # PHASE 1: UNDERSTAND & THINK
    # =========================================
    print("[1/8] UNDERSTAND & THINK: PM designing analysis plan...")

    pm = ProjectManager(PROJECT_ROOT)
    plan = pm.design_plan(commodity)

    log_event(log_path, "PM", "Design Plan", "Complete",
              f"Commodity: {commodity}, Modules: {len(plan.modules)}")

    print(f"      Plan created: {len(plan.modules)} modules, parallel={plan.parallel_execution}")

    # =========================================
    # PHASE 2: PLAN - SUP & APPROVAL Review
    # =========================================
    print("[2/8] PLAN: SUP reviewing plan...")

    sup = Supervisor(PROJECT_ROOT)
    from dataclasses import asdict
    sup_validation = sup.validate_plan(asdict(plan))
    sup.save_review(commodity, sup_validation)

    log_event(log_path, "SUP", "Validate Plan", sup_validation.status,
              f"Issues: {len(sup_validation.issues)}")

    print(f"      SUP validation: {sup_validation.status}")

    print("[3/8] PLAN: APPROVAL verifying against blueprint...")

    approval = ApprovalAgent(PROJECT_ROOT)
    plan_approval = approval.verify_plan_against_blueprint(asdict(plan))
    approval.save_approval(commodity, plan_approval)

    log_event(log_path, "APPROVAL", "Verify Plan", plan_approval.decision,
              f"Score: {plan_approval.final_score}")

    print(f"      APPROVAL decision: {plan_approval.decision}")

    if plan_approval.decision == "REJECTED":
        print("\n[!] Plan REJECTED by APPROVAL agent. Aborting.")
        return None

    # =========================================
    # PHASE 3: USER APPROVAL GATE (Hard Rule #6)
    # =========================================
    print("\n[4/9] USER APPROVAL GATE (Hard Rule #6)")
    print("=" * 60)

    # Display Flowchart
    print("""
    EXECUTION FLOWCHART:
    ====================

    USER REQUEST: Analyze {commodity}
           |
           v
    +------------------+
    | LEVEL 1: PM      |  <-- COMPLETED
    | Design Plan      |      Plan: {modules} modules
    +------------------+
           |
           v
    +------------------+
    | LEVEL 1: SUP     |  <-- COMPLETED
    | Challenge Plan   |      Status: {sup_status}
    +------------------+
           |
           v
    +------------------+
    | LEVEL 1: APPROVAL|  <-- COMPLETED
    | Verify Blueprint |      Decision: {approval_decision}
    +------------------+
           |
           v
    +==================+
    | USER APPROVAL    |  <-- YOU ARE HERE
    | Approve to       |
    | proceed?         |
    +==================+
           |
           v (if approved)
    +------------------+
    | LEVEL 2: EXECUTE |  6 Task Managers in parallel
    | TM-FUND, TM-NEWS |  Each with 2 debate rounds
    | TM-VIEWS, TM-TECH|  SUP-A + SUP-B validation
    | TM-STRUCT, TM-POS|
    +------------------+
           |
           v
    +------------------+
    | TM-REPORT        |  Synthesize HTML report
    | Generate HTML    |  with candlestick chart
    +------------------+
           |
           v
    +------------------+
    | FINAL REVIEW     |  SUP + APPROVAL verify
    +------------------+
           |
           v
    +------------------+
    | HOUSEKEEPER      |  Cleanup per tidyup.md
    +------------------+
           |
           v
    DELIVERABLE: output/{commodity}.html
    """.format(
        commodity=commodity.upper(),
        modules=len(plan.modules),
        sup_status=sup_validation.status,
        approval_decision=plan_approval.decision
    ))

    # Display Detailed Plan
    print("\n    DETAILED PLAN:")
    print("    " + "=" * 50)
    print(f"    Commodity: {commodity.upper()}")
    print(f"    Execution Mode: {'Parallel' if parallel else 'Sequential'}")
    print(f"    Data Mode: {'FRESH (Internet fetch)' if force_refresh else 'Cached (if available)'}")
    print(f"    Debate Rounds: {plan.debate_rounds_min} minimum per module")
    print(f"\n    Modules to Execute:")
    for i, module in enumerate(plan.modules, 1):
        print(f"      {i}. {module.upper()}")
    print(f"\n    Data Sources:")
    for source in plan.data_sources:
        print(f"      - {source}")
    print(f"\n    Output Path: {plan.output_path}")
    print(f"\n    SUP Validation:")
    print(f"      - Status: {sup_validation.status}")
    print(f"      - Issues: {len(sup_validation.issues)}")
    for issue in sup_validation.issues[:3]:
        print(f"        * {issue}")
    print(f"\n    APPROVAL Checks Passed:")
    for check in plan_approval.checks_passed:
        print(f"      [OK] {check}")
    if plan_approval.conditions:
        print(f"\n    Conditions:")
        for cond in plan_approval.conditions:
            print(f"      ! {cond}")
    print("    " + "=" * 50)

    # Ask for User Approval
    print("\n" + "=" * 60)
    user_input = input("    Approve to proceed? (yes/no): ").strip().lower()

    if user_input not in ['yes', 'y']:
        print("\n[!] User did not approve. Aborting execution.")
        log_event(log_path, "USER", "Approval Gate", "REJECTED",
                  "User declined to proceed")
        return None

    log_event(log_path, "USER", "Approval Gate", "APPROVED",
              "User approved execution")
    print("\n    User APPROVED. Proceeding with execution...")
    print("=" * 60)

    # =========================================
    # PHASE 4: EXECUTE - Level 2 Modules (Parallel)
    # =========================================
    print(f"\n[5/9] EXECUTE: Running Level 2 modules {'in parallel' if parallel else 'sequentially'}...")

    # Task Manager instances
    task_managers = {
        "tm_fund": FundamentalsManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
        "tm_news": NewsManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
        "tm_views": ViewsManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
        "tm_tech": TechnicalManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
        "tm_struct": StructureManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
        "tm_pos": PositioningManager(PROJECT_ROOT, commodity, force_refresh=force_refresh),
    }

    results = {}

    if parallel:
        # Run in parallel
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(tm.run): name
                for name, tm in task_managers.items()
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()
                    results[name] = result
                    print(f"      [{name}] Score: {result.score:+.1f}, Confidence: {result.confidence:.0%}")
                    log_event(log_path, name.upper(), "Analysis Complete", "Complete",
                              f"Score: {result.score:+.1f}, Debate rounds: {result.debate_rounds}")
                except Exception as e:
                    print(f"      [{name}] ERROR: {e}")
                    results[name] = {"error": str(e)}
    else:
        # Run sequentially
        for name, tm in task_managers.items():
            try:
                result = tm.run()
                results[name] = result
                print(f"      [{name}] Score: {result.score:+.1f}")
            except Exception as e:
                print(f"      [{name}] ERROR: {e}")
                results[name] = {"error": str(e)}

    # =========================================
    # PHASE 5: SYNTHESIZE - Generate Report
    # =========================================
    print("\n[6/9] SYNTHESIZE: TM-REPORT generating HTML...")

    report_manager = ReportManager(PROJECT_ROOT, commodity)
    report_result = report_manager.run()

    log_event(log_path, "TM-REPORT", "Generate HTML", "Complete",
              f"Output: {report_result.get('output_path')}")

    print(f"      Report generated: {report_result.get('output_path')}")
    print(f"      Weighted score: {report_result['synthesis']['weighted_score']:+.1f}")
    print(f"      Interpretation: {report_result['synthesis']['interpretation']}")

    # =========================================
    # PHASE 6: REVIEW - Final Validation
    # =========================================
    print("\n[7/9] REVIEW: SUP + APPROVAL final check...")

    # Collect module outputs for review
    module_outputs = report_manager.collect_module_outputs()

    final_validation = sup.validate_final_report(
        report_result['synthesis'],
        module_outputs
    )

    final_approval = approval.verify_report_for_delivery(
        commodity,
        report_result['synthesis'],
        asdict(final_validation)
    )
    approval.save_approval(commodity, final_approval)

    log_event(log_path, "SUP+APPROVAL", "Final Review", final_approval.decision,
              f"Ready for delivery: {final_approval.ready_for_delivery}")

    print(f"      Final approval: {final_approval.decision}")

    # =========================================
    # PHASE 7: DELIVER
    # =========================================
    print("\n[8/9] DELIVER: Report ready")
    print(f"      Output: {report_result.get('output_path')}")

    # =========================================
    # PHASE 8: CLEANUP - Housekeeper
    # =========================================
    print("\n[9/9] CLEANUP: HOUSEKEEPER running...")

    housekeeper = Housekeeper(PROJECT_ROOT)
    cleanup_result = housekeeper.run()

    print(f"      Cleanup complete: {len(cleanup_result['actions'])} actions")

    # =========================================
    # SUMMARY
    # =========================================
    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE: {commodity.upper()}")
    print(f"{'='*60}")
    print(f"  Weighted Score: {report_result['synthesis']['weighted_score']:+.1f}")
    print(f"  Interpretation: {report_result['synthesis']['interpretation']}")
    print(f"  Modules: {report_result['synthesis']['modules_included']}/6")
    print(f"  Report: {report_result.get('output_path')}")
    print(f"{'='*60}\n")

    return report_result


def main():
    parser = argparse.ArgumentParser(
        description="CommodityTrading Multi-Agent Analysis System"
    )
    parser.add_argument(
        "commodity",
        nargs="?",
        help="Commodity to analyze (e.g., aluminum, copper)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available commodities"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run modules sequentially instead of parallel"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Force fresh data fetch from internet (bypass cache)"
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable commodities:")
        for c in COMMODITIES:
            print(f"  - {c}")
        print()
        return

    if not args.commodity:
        parser.print_help()
        print("\nExample: python run.py aluminum")
        return

    commodity = args.commodity.lower().replace(" ", "_")

    if commodity not in COMMODITIES:
        print(f"\nWarning: '{commodity}' not in standard list.")
        print("Proceeding anyway (may have limited data)...\n")

    run_analysis(commodity, parallel=not args.sequential, force_refresh=args.fresh)


if __name__ == "__main__":
    main()
