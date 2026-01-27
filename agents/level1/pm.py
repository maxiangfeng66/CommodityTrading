"""
Project Manager (PM) Agent
Level 1 Strategic Agent - Design & Coordinate
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class AnalysisPlan:
    """Analysis plan created by PM"""
    commodity: str
    created_at: str
    modules: List[str]
    data_sources: List[str]
    output_path: str
    parallel_execution: bool
    debate_rounds_min: int
    status: str = "pending"


class ProjectManager:
    """
    Project Manager Agent (PM)
    Responsibilities:
    - Design analysis plan
    - Allocate tasks to Level 2 agents
    - Coordinate parallel execution
    - Synthesize final output
    """

    MODULES = [
        "tm_fund",    # Fundamentals
        "tm_news",    # News & Policy
        "tm_views",   # Market Views
        "tm_tech",    # Technical Analysis
        "tm_struct",  # Market Structure
        "tm_pos",     # Positioning
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules_dir = project_root / "modules"
        self.output_dir = project_root / "output"
        self.brain_dir = project_root / "brain"

    def design_plan(self, commodity: str) -> AnalysisPlan:
        """
        Design the analysis plan for a commodity.
        This is the first step - understand and think before execute.
        """
        commodity_key = commodity.lower().replace(" ", "_")
        commodity_dir = self.modules_dir / commodity_key
        commodity_dir.mkdir(parents=True, exist_ok=True)

        plan = AnalysisPlan(
            commodity=commodity,
            created_at=datetime.now().isoformat(),
            modules=self.MODULES,
            data_sources=[
                "Yahoo Finance (prices)",
                "CFTC (COT reports)",
                "LME (warehouse stocks)",
                "World Bank (fundamentals)",
                "News aggregators",
            ],
            output_path=str(self.output_dir / f"{commodity_key}.html"),
            parallel_execution=True,
            debate_rounds_min=2,
            status="designed"
        )

        # Save plan
        plan_path = commodity_dir / "pm_design.json"
        with open(plan_path, 'w') as f:
            json.dump(asdict(plan), f, indent=2)

        return plan

    def allocate_tasks(self, plan: AnalysisPlan) -> Dict[str, Dict]:
        """
        Allocate tasks to Level 2 Task Managers.
        Each TM gets specific scope and data requirements.
        """
        commodity_key = plan.commodity.lower().replace(" ", "_")

        tasks = {
            "tm_fund": {
                "module": "tm_fund",
                "commodity": plan.commodity,
                "scope": "Fundamentals analysis",
                "requirements": [
                    "Supply/demand balance",
                    "Production forecasts",
                    "Inventory levels",
                    "Seasonal patterns",
                ],
                "data_sources": ["World Bank", "Industry associations"],
                "output_file": f"modules/{commodity_key}/fund_output.json",
                "debate_file": f"modules/{commodity_key}/fund_debate.md",
            },
            "tm_news": {
                "module": "tm_news",
                "commodity": plan.commodity,
                "scope": "News & Policy analysis",
                "requirements": [
                    "Recent policy changes",
                    "Weather impacts",
                    "Trade developments",
                    "Market-moving events",
                ],
                "data_sources": ["News aggregators", "Government sources"],
                "output_file": f"modules/{commodity_key}/news_output.json",
                "debate_file": f"modules/{commodity_key}/news_debate.md",
            },
            "tm_views": {
                "module": "tm_views",
                "commodity": plan.commodity,
                "scope": "Market Views analysis",
                "requirements": [
                    "Consensus positioning",
                    "Analyst forecasts",
                    "Logic soundness assessment",
                    "Contrarian signals",
                ],
                "data_sources": ["Analyst reports", "Market commentary"],
                "output_file": f"modules/{commodity_key}/views_output.json",
                "debate_file": f"modules/{commodity_key}/views_debate.md",
            },
            "tm_tech": {
                "module": "tm_tech",
                "commodity": plan.commodity,
                "scope": "Technical Analysis",
                "requirements": [
                    "Trend indicators (60MA, 200MA)",
                    "Momentum signals (RSI, MACD)",
                    "Support/resistance levels",
                    "Key technical triggers",
                ],
                "data_sources": ["Yahoo Finance"],
                "output_file": f"modules/{commodity_key}/tech_output.json",
                "debate_file": f"modules/{commodity_key}/tech_debate.md",
            },
            "tm_struct": {
                "module": "tm_struct",
                "commodity": plan.commodity,
                "scope": "Market Structure analysis",
                "requirements": [
                    "Volume patterns",
                    "Open Interest analysis",
                    "Market attention metrics",
                    "Liquidity assessment",
                ],
                "data_sources": ["Exchange data", "Yahoo Finance"],
                "output_file": f"modules/{commodity_key}/struct_output.json",
                "debate_file": f"modules/{commodity_key}/struct_debate.md",
            },
            "tm_pos": {
                "module": "tm_pos",
                "commodity": plan.commodity,
                "scope": "Positioning analysis",
                "requirements": [
                    "COT report analysis",
                    "Non-commercial positioning",
                    "CTA positioning estimates",
                    "Crowding metrics",
                ],
                "data_sources": ["CFTC COT reports"],
                "output_file": f"modules/{commodity_key}/pos_output.json",
                "debate_file": f"modules/{commodity_key}/pos_debate.md",
            },
        }

        return tasks

    def coordinate_execution(self, tasks: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Coordinate the execution of Level 2 tasks.
        Returns execution status for each module.
        """
        execution_status = {
            "start_time": datetime.now().isoformat(),
            "parallel": True,
            "tasks": {},
        }

        for module, task in tasks.items():
            execution_status["tasks"][module] = {
                "status": "pending",
                "assigned_at": datetime.now().isoformat(),
            }

        return execution_status

    def collect_results(self, commodity: str) -> Dict[str, Any]:
        """
        Collect results from all Level 2 modules.
        """
        commodity_key = commodity.lower().replace(" ", "_")
        commodity_dir = self.modules_dir / commodity_key

        results = {}
        for module in self.MODULES:
            output_file = commodity_dir / f"{module.replace('tm_', '')}_output.json"
            if output_file.exists():
                with open(output_file, 'r') as f:
                    results[module] = json.load(f)
            else:
                results[module] = {"status": "not_found"}

        return results

    def synthesize_final(self, commodity: str, results: Dict[str, Any]) -> Dict:
        """
        Synthesize final analysis from all module results.
        """
        # Calculate weighted score
        scores = []
        weights = []

        score_map = {
            "tm_fund": 1.5,   # Fundamentals weighted higher
            "tm_news": 1.0,
            "tm_views": 1.0,
            "tm_tech": 1.2,
            "tm_struct": 0.8,
            "tm_pos": 1.0,
        }

        for module, result in results.items():
            if isinstance(result, dict) and "score" in result:
                scores.append(result["score"])
                weights.append(score_map.get(module, 1.0))

        weighted_score = None
        if scores and weights:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

        synthesis = {
            "commodity": commodity,
            "synthesized_at": datetime.now().isoformat(),
            "modules_completed": len([r for r in results.values() if isinstance(r, dict) and r.get("status") != "not_found"]),
            "total_modules": len(self.MODULES),
            "weighted_score": round(weighted_score, 2) if weighted_score else None,
            "interpretation": self._interpret_score(weighted_score) if weighted_score else "Insufficient data",
            "module_summaries": {
                module: result.get("summary", "N/A") if isinstance(result, dict) else "N/A"
                for module, result in results.items()
            },
        }

        return synthesis

    def _interpret_score(self, score: float) -> str:
        """Interpret the weighted score"""
        if score <= -3:
            return "Strongly Bearish"
        elif score <= -1:
            return "Bearish"
        elif score <= 1:
            return "Neutral"
        elif score <= 3:
            return "Bullish"
        else:
            return "Strongly Bullish"
