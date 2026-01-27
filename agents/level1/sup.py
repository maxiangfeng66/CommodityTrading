"""
Supervisor (SUP) Agent
Level 1 Strategic Agent - Challenge & Validate
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Result of supervisor validation"""
    validated_at: str
    item_type: str  # "plan", "analysis", "report"
    status: str  # "approved", "rejected", "needs_revision"
    issues: List[Dict]
    recommendations: List[str]
    confidence: float


class Supervisor:
    """
    Supervisor Agent (SUP)
    Responsibilities:
    - Challenge PM decisions step-by-step
    - Validate logic and completeness
    - Review module outputs
    - Ensure quality standards
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.brain_dir = project_root / "brain"

    def validate_plan(self, plan: Dict) -> ValidationResult:
        """
        Validate PM's analysis plan against requirements.
        """
        issues = []
        recommendations = []

        # Check required fields
        required_fields = ["commodity", "modules", "data_sources", "output_path"]
        for field in required_fields:
            if field not in plan:
                issues.append({
                    "severity": "high",
                    "field": field,
                    "issue": f"Missing required field: {field}",
                })

        # Check module coverage
        expected_modules = ["tm_fund", "tm_news", "tm_views", "tm_tech", "tm_struct", "tm_pos"]
        plan_modules = plan.get("modules", [])
        missing_modules = [m for m in expected_modules if m not in plan_modules]
        if missing_modules:
            issues.append({
                "severity": "medium",
                "field": "modules",
                "issue": f"Missing modules: {missing_modules}",
            })

        # Check data sources
        if len(plan.get("data_sources", [])) < 3:
            recommendations.append("Consider adding more data sources for robustness")

        # Check debate rounds
        if plan.get("debate_rounds_min", 0) < 2:
            issues.append({
                "severity": "medium",
                "field": "debate_rounds_min",
                "issue": "Minimum debate rounds should be 2 per blueprint",
            })

        # Determine status
        high_issues = [i for i in issues if i["severity"] == "high"]
        status = "rejected" if high_issues else ("needs_revision" if issues else "approved")
        confidence = 0.9 if not issues else (0.6 if high_issues else 0.75)

        result = ValidationResult(
            validated_at=datetime.now().isoformat(),
            item_type="plan",
            status=status,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence
        )

        return result

    def validate_module_output(self, module: str, output: Dict) -> ValidationResult:
        """
        Validate a Level 2 module's output.
        """
        issues = []
        recommendations = []

        # Check required output fields
        required_fields = ["module", "commodity", "score", "confidence", "analysis", "sources"]
        for field in required_fields:
            if field not in output:
                issues.append({
                    "severity": "high" if field in ["score", "analysis"] else "medium",
                    "field": field,
                    "issue": f"Missing required field: {field}",
                })

        # Validate score range
        score = output.get("score")
        if score is not None:
            if not -5 <= score <= 5:
                issues.append({
                    "severity": "high",
                    "field": "score",
                    "issue": f"Score {score} outside valid range [-5, 5]",
                })

        # Validate confidence
        confidence = output.get("confidence")
        if confidence is not None:
            if not 0 <= confidence <= 1:
                issues.append({
                    "severity": "medium",
                    "field": "confidence",
                    "issue": f"Confidence {confidence} outside valid range [0, 1]",
                })

        # Check sources
        sources = output.get("sources", [])
        if len(sources) < 2:
            recommendations.append("Add more data sources to improve reliability")

        # Check analysis depth
        analysis = output.get("analysis", {})
        if isinstance(analysis, dict) and len(analysis) < 3:
            recommendations.append("Analysis could be more comprehensive")

        # Determine status
        high_issues = [i for i in issues if i["severity"] == "high"]
        status = "rejected" if high_issues else ("needs_revision" if issues else "approved")
        result_confidence = 0.9 if not issues else (0.5 if high_issues else 0.7)

        result = ValidationResult(
            validated_at=datetime.now().isoformat(),
            item_type=f"module_{module}",
            status=status,
            issues=issues,
            recommendations=recommendations,
            confidence=result_confidence
        )

        return result

    def validate_final_report(self, synthesis: Dict, results: Dict) -> ValidationResult:
        """
        Validate the final synthesized report before delivery.
        """
        issues = []
        recommendations = []

        # Check synthesis completeness
        modules_completed = synthesis.get("modules_completed", 0)
        total_modules = synthesis.get("total_modules", 6)

        if modules_completed < total_modules:
            issues.append({
                "severity": "high" if modules_completed < 4 else "medium",
                "field": "modules_completed",
                "issue": f"Only {modules_completed}/{total_modules} modules completed",
            })

        # Check weighted score
        if synthesis.get("weighted_score") is None:
            issues.append({
                "severity": "high",
                "field": "weighted_score",
                "issue": "No weighted score calculated",
            })

        # Check individual module quality
        for module, result in results.items():
            if isinstance(result, dict):
                if result.get("confidence", 0) < 0.5:
                    recommendations.append(f"Module {module} has low confidence - review data quality")

        # Consistency check between modules
        scores = [
            r.get("score") for r in results.values()
            if isinstance(r, dict) and r.get("score") is not None
        ]
        if scores:
            score_range = max(scores) - min(scores)
            if score_range > 6:
                issues.append({
                    "severity": "medium",
                    "field": "consistency",
                    "issue": f"Large score dispersion ({score_range}) between modules - review for conflicts",
                })

        # Determine status
        high_issues = [i for i in issues if i["severity"] == "high"]
        status = "rejected" if high_issues else ("needs_revision" if issues else "approved")
        confidence = 0.9 if not issues else (0.5 if high_issues else 0.7)

        result = ValidationResult(
            validated_at=datetime.now().isoformat(),
            item_type="final_report",
            status=status,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence
        )

        return result

    def save_review(self, commodity: str, review: ValidationResult):
        """Save review to file"""
        commodity_key = commodity.lower().replace(" ", "_")
        review_dir = self.project_root / "modules" / commodity_key
        review_dir.mkdir(parents=True, exist_ok=True)

        review_path = review_dir / "sup_review.json"
        with open(review_path, 'w') as f:
            json.dump(asdict(review), f, indent=2)
