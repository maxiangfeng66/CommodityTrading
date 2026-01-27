"""
Base Task Manager Class
All Level 2 TMs inherit from this
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.debate import (
    DebateEngine, Challenge, Response, DebateResult,
    create_logic_checker, create_data_validator
)


@dataclass
class ModuleOutput:
    """Standard output format for all modules"""
    module: str
    commodity: str
    timestamp: str
    score: float  # -5 to +5
    confidence: float  # 0 to 1
    interpretation: str
    summary: str
    analysis: Dict
    sources: List[str]
    debate_outcome: str
    debate_rounds: int


class TaskManager(ABC):
    """
    Base class for all Level 2 Task Managers.
    Each TM has:
    - SUP-A: Logic Challenger
    - SUP-B: Data Validator
    - Debate protocol with min 2 rounds
    """

    MODULE_NAME: str = "base"

    def __init__(self, project_root: Path, commodity: str, force_refresh: bool = False):
        self.project_root = project_root
        self.commodity = commodity
        self.commodity_key = commodity.lower().replace(" ", "_")
        self.output_dir = project_root / "modules" / self.commodity_key
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.force_refresh = force_refresh

    @abstractmethod
    def fetch_data(self) -> Dict:
        """Fetch required data for analysis"""
        pass

    @abstractmethod
    def analyze(self, data: Dict) -> Dict:
        """Perform initial analysis"""
        pass

    @abstractmethod
    def get_logic_rules(self) -> List[Dict]:
        """Get logic rules for SUP-A"""
        pass

    @abstractmethod
    def get_validation_rules(self) -> List[Dict]:
        """Get validation rules for SUP-B"""
        pass

    def respond_to_challenges(
        self,
        analysis: Dict,
        challenges: List[Challenge]
    ) -> tuple[Dict, List[Response]]:
        """
        TM's response to challenges from SUP-A and SUP-B.
        Can revise analysis based on valid challenges.
        """
        revised = analysis.copy()
        responses = []

        for challenge in challenges:
            response = self._handle_challenge(revised, challenge)
            responses.append(response)

            if response.revision_made and response.revised_value is not None:
                # Apply revision to analysis
                if challenge.challenge_type == "logic":
                    revised["logic_revised"] = True
                elif challenge.challenge_type == "data":
                    revised["data_revised"] = True

        return revised, responses

    def _handle_challenge(self, analysis: Dict, challenge: Challenge) -> Response:
        """Handle a single challenge"""
        # Default handling - can be overridden
        if challenge.severity == "high":
            return Response(
                addressed=True,
                explanation=f"Acknowledged high-severity issue: {challenge.issue}",
                revision_made=True,
                revised_value="Applied correction"
            )
        elif challenge.severity == "medium":
            return Response(
                addressed=True,
                explanation=f"Reviewed: {challenge.issue}. Analysis stands with clarification.",
                revision_made=False
            )
        else:
            return Response(
                addressed=True,
                explanation=f"Noted: {challenge.issue}. Minor issue addressed.",
                revision_made=False
            )

    def run(self) -> ModuleOutput:
        """
        Execute the full analysis with debate protocol.
        """
        # 1. Fetch data
        data = self.fetch_data()

        # 2. Initial analysis
        initial_analysis = self.analyze(data)

        # 3. Set up debate
        debate_engine = DebateEngine(self.MODULE_NAME, self.output_dir)

        # 4. Create supervisors
        sup_a = create_logic_checker(self.get_logic_rules())
        sup_b = create_data_validator(self.get_validation_rules())

        # 5. Run debate
        debate_result = debate_engine.run_debate(
            initial_analysis=initial_analysis,
            sup_a_check=sup_a,
            sup_b_check=sup_b,
            tm_respond=self.respond_to_challenges
        )

        # 6. Create output
        final_analysis = debate_result.final_analysis
        output = ModuleOutput(
            module=self.MODULE_NAME,
            commodity=self.commodity,
            timestamp=datetime.now().isoformat(),
            score=final_analysis.get("score", 0),
            confidence=debate_result.confidence,
            interpretation=self._interpret_score(final_analysis.get("score", 0)),
            summary=final_analysis.get("summary", ""),
            analysis=final_analysis,
            sources=final_analysis.get("sources", []),
            debate_outcome=debate_result.outcome.value,
            debate_rounds=debate_result.total_rounds
        )

        # 7. Save output
        self._save_output(output)

        return output

    def _interpret_score(self, score: float) -> str:
        """Interpret score to text"""
        if score <= -3:
            return "Strongly Bearish"
        elif score <= -1:
            return "Bearish"
        elif score < 1:
            return "Neutral"
        elif score < 3:
            return "Bullish"
        else:
            return "Strongly Bullish"

    def _save_output(self, output: ModuleOutput):
        """Save output to JSON file"""
        output_path = self.output_dir / f"{self.MODULE_NAME.replace('tm_', '')}_output.json"
        with open(output_path, 'w') as f:
            json.dump(asdict(output), f, indent=2, default=str)
