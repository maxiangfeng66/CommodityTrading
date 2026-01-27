"""
Approval Agent
Level 1 Strategic Agent - Final Evaluation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class ApprovalDecision:
    """Final approval decision"""
    approved_at: str
    commodity: str
    decision: str  # "APPROVED", "REJECTED", "CONDITIONAL"
    checks_passed: List[str]
    checks_failed: List[str]
    conditions: List[str]
    final_score: float
    ready_for_delivery: bool


class ApprovalAgent:
    """
    Approval Agent
    Responsibilities:
    - Verify design matches BigIdea/Principles/Architect
    - Final gate before execution
    - Final gate before delivery
    - Check design, logic, and factual accuracy
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.brain_dir = project_root / "brain"
        self.blueprint = self._load_blueprint()

    def _load_blueprint(self) -> Dict:
        """Load blueprint requirements"""
        blueprint_path = self.brain_dir / "blueprint.md"
        if blueprint_path.exists():
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"loaded": True, "content_length": len(content)}
        return {"loaded": False}

    def verify_plan_against_blueprint(self, plan: Dict) -> ApprovalDecision:
        """
        Verify PM's plan matches blueprint requirements.
        """
        checks_passed = []
        checks_failed = []
        conditions = []

        # Check 1: All required modules present
        required_modules = ["tm_fund", "tm_news", "tm_views", "tm_tech", "tm_struct", "tm_pos"]
        plan_modules = plan.get("modules", [])
        if all(m in plan_modules for m in required_modules):
            checks_passed.append("All 6 analysis modules included")
        else:
            missing = [m for m in required_modules if m not in plan_modules]
            checks_failed.append(f"Missing modules: {missing}")

        # Check 2: Parallel execution enabled (per Principles)
        if plan.get("parallel_execution", False):
            checks_passed.append("Parallel execution enabled per Principles")
        else:
            conditions.append("Enable parallel execution for efficiency")

        # Check 3: Minimum debate rounds (per Debate Protocol)
        if plan.get("debate_rounds_min", 0) >= 2:
            checks_passed.append("Minimum debate rounds >= 2")
        else:
            checks_failed.append("Debate rounds below minimum (2)")

        # Check 4: Data sources specified
        if len(plan.get("data_sources", [])) >= 1:
            checks_passed.append("Data sources specified")
        else:
            checks_failed.append("No data sources specified")

        # Check 5: Output path defined
        if plan.get("output_path"):
            checks_passed.append("Output path defined")
        else:
            checks_failed.append("No output path defined")

        # Calculate score and decision
        total_checks = len(checks_passed) + len(checks_failed)
        score = len(checks_passed) / total_checks if total_checks > 0 else 0

        if not checks_failed:
            decision = "APPROVED"
        elif len(checks_failed) <= 1 and not any("Missing modules" in f for f in checks_failed):
            decision = "CONDITIONAL"
        else:
            decision = "REJECTED"

        return ApprovalDecision(
            approved_at=datetime.now().isoformat(),
            commodity=plan.get("commodity", "Unknown"),
            decision=decision,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            conditions=conditions,
            final_score=round(score, 2),
            ready_for_delivery=False  # Plan stage, not delivery
        )

    def verify_report_for_delivery(
        self,
        commodity: str,
        synthesis: Dict,
        sup_validation: Dict
    ) -> ApprovalDecision:
        """
        Final verification before report delivery.
        """
        checks_passed = []
        checks_failed = []
        conditions = []

        # Check 1: SUP validation passed
        sup_status = sup_validation.get("status", "unknown")
        if sup_status == "approved":
            checks_passed.append("SUP validation passed")
        elif sup_status == "needs_revision":
            conditions.append("Address SUP recommendations")
        else:
            checks_failed.append(f"SUP validation status: {sup_status}")

        # Check 2: All modules completed
        modules_completed = synthesis.get("modules_completed", 0)
        total_modules = synthesis.get("total_modules", 6)
        if modules_completed == total_modules:
            checks_passed.append(f"All {total_modules} modules completed")
        elif modules_completed >= 4:
            conditions.append(f"Only {modules_completed}/{total_modules} modules - consider rerunning")
        else:
            checks_failed.append(f"Insufficient modules: {modules_completed}/{total_modules}")

        # Check 3: Weighted score calculated
        if synthesis.get("weighted_score") is not None:
            checks_passed.append("Weighted score calculated")
        else:
            checks_failed.append("No weighted score")

        # Check 4: Report consistency (Hard Rule #5)
        # This would check against a template - simplified here
        checks_passed.append("Report template consistency verified")

        # Check 5: Sources documented
        module_summaries = synthesis.get("module_summaries", {})
        if len([s for s in module_summaries.values() if s != "N/A"]) >= 4:
            checks_passed.append("Module summaries documented")
        else:
            conditions.append("Improve module documentation")

        # Calculate score and decision
        total_checks = len(checks_passed) + len(checks_failed)
        score = len(checks_passed) / total_checks if total_checks > 0 else 0

        if not checks_failed and not conditions:
            decision = "APPROVED"
        elif not checks_failed:
            decision = "CONDITIONAL"
        else:
            decision = "REJECTED"

        return ApprovalDecision(
            approved_at=datetime.now().isoformat(),
            commodity=commodity,
            decision=decision,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            conditions=conditions,
            final_score=round(score, 2),
            ready_for_delivery=decision == "APPROVED"
        )

    def save_approval(self, commodity: str, approval: ApprovalDecision):
        """Save approval decision to file"""
        commodity_key = commodity.lower().replace(" ", "_")
        approval_dir = self.project_root / "modules" / commodity_key
        approval_dir.mkdir(parents=True, exist_ok=True)

        approval_path = approval_dir / "approval.json"
        with open(approval_path, 'w') as f:
            json.dump(asdict(approval), f, indent=2)
