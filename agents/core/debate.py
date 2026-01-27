"""
Debate Protocol Engine
Implements the debate protocol between Task Managers and Supervisors
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class DebateOutcome(Enum):
    ACCEPTED = "accepted"
    REVISED = "revised"
    ESCALATED = "escalated"


@dataclass
class Challenge:
    """A challenge raised by a supervisor"""
    challenger: str  # SUP-A or SUP-B
    challenge_type: str  # "logic" or "data"
    issue: str
    severity: str  # "low", "medium", "high"
    suggested_action: str


@dataclass
class Response:
    """Task Manager's response to a challenge"""
    addressed: bool
    explanation: str
    revision_made: bool
    revised_value: Any = None


@dataclass
class DebateRound:
    """A single round of debate"""
    round_number: int
    tm_analysis: Dict
    challenges: List[Challenge]
    responses: List[Response]
    outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DebateResult:
    """Final result of a debate"""
    module: str
    initial_analysis: Dict
    final_analysis: Dict
    rounds: List[DebateRound]
    total_rounds: int
    outcome: DebateOutcome
    confidence: float
    escalated_to: Optional[str] = None


class DebateEngine:
    """
    Orchestrates debates between Task Managers and Supervisors.

    Protocol:
    1. TM presents initial analysis
    2. SUP-A challenges logic/assumptions
    3. TM responds with clarifications
    4. SUP-B validates data/methodology
    5. Iterate (min 2 rounds, more if disagreement)
    6. Escalate to Level 1 SUP if unresolved after 3 rounds
    """

    MIN_ROUNDS = 2
    MAX_ROUNDS = 5
    ESCALATION_THRESHOLD = 3

    def __init__(self, module_name: str, output_dir: Path):
        self.module_name = module_name
        self.output_dir = output_dir
        self.rounds: List[DebateRound] = []

    def run_debate(
        self,
        initial_analysis: Dict,
        sup_a_check: Callable[[Dict], List[Challenge]],
        sup_b_check: Callable[[Dict], List[Challenge]],
        tm_respond: Callable[[Dict, List[Challenge]], tuple[Dict, List[Response]]],
    ) -> DebateResult:
        """
        Run the full debate protocol.

        Args:
            initial_analysis: TM's initial analysis output
            sup_a_check: SUP-A's logic checking function
            sup_b_check: SUP-B's data validation function
            tm_respond: TM's response function that handles challenges

        Returns:
            DebateResult with final analysis and debate history
        """
        current_analysis = initial_analysis.copy()
        outcome = DebateOutcome.REVISED

        for round_num in range(1, self.MAX_ROUNDS + 1):
            # SUP-A challenges logic
            logic_challenges = sup_a_check(current_analysis)

            # SUP-B validates data
            data_challenges = sup_b_check(current_analysis)

            all_challenges = logic_challenges + data_challenges

            # If no challenges, accept
            if not all_challenges and round_num >= self.MIN_ROUNDS:
                round_result = DebateRound(
                    round_number=round_num,
                    tm_analysis=current_analysis,
                    challenges=[],
                    responses=[],
                    outcome="accepted_no_challenges"
                )
                self.rounds.append(round_result)
                outcome = DebateOutcome.ACCEPTED
                break

            # TM responds to challenges
            revised_analysis, responses = tm_respond(current_analysis, all_challenges)

            # Create round record
            round_result = DebateRound(
                round_number=round_num,
                tm_analysis=current_analysis,
                challenges=[asdict(c) for c in all_challenges],
                responses=[asdict(r) for r in responses],
                outcome="revised" if any(r.revision_made for r in responses) else "defended"
            )
            self.rounds.append(round_result)

            # Check if all challenges addressed
            high_severity_unaddressed = [
                c for c, r in zip(all_challenges, responses)
                if c.severity == "high" and not r.addressed
            ]

            if high_severity_unaddressed and round_num >= self.ESCALATION_THRESHOLD:
                outcome = DebateOutcome.ESCALATED
                break

            # Update analysis for next round
            current_analysis = revised_analysis

            # If all addressed and min rounds complete, accept
            if all(r.addressed for r in responses) and round_num >= self.MIN_ROUNDS:
                outcome = DebateOutcome.ACCEPTED
                break

        # Calculate confidence based on debate
        confidence = self._calculate_confidence(outcome, self.rounds)

        result = DebateResult(
            module=self.module_name,
            initial_analysis=initial_analysis,
            final_analysis=current_analysis,
            rounds=self.rounds,
            total_rounds=len(self.rounds),
            outcome=outcome,
            confidence=confidence,
            escalated_to="Level1-SUP" if outcome == DebateOutcome.ESCALATED else None
        )

        # Save debate log
        self._save_debate_log(result)

        return result

    def _calculate_confidence(self, outcome: DebateOutcome, rounds: List[DebateRound]) -> float:
        """Calculate confidence score based on debate outcome"""
        base_confidence = 0.7

        if outcome == DebateOutcome.ACCEPTED:
            base_confidence = 0.85
        elif outcome == DebateOutcome.ESCALATED:
            base_confidence = 0.5

        # Adjust based on number of rounds
        if len(rounds) <= 2:
            base_confidence += 0.1
        elif len(rounds) >= 4:
            base_confidence -= 0.1

        # Adjust based on challenges addressed
        total_challenges = sum(len(r.challenges) for r in rounds)
        addressed = sum(
            1 for r in rounds
            for resp in r.responses
            if isinstance(resp, dict) and resp.get("addressed")
        )

        if total_challenges > 0:
            address_ratio = addressed / total_challenges
            base_confidence += (address_ratio - 0.5) * 0.2

        return min(0.95, max(0.3, round(base_confidence, 2)))

    def _save_debate_log(self, result: DebateResult):
        """Save debate log to markdown file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.output_dir / f"{self.module_name}_debate.md"

        with open(log_path, 'w') as f:
            f.write(f"# Debate Log: {self.module_name}\n\n")
            f.write(f"**Outcome:** {result.outcome.value}\n")
            f.write(f"**Total Rounds:** {result.total_rounds}\n")
            f.write(f"**Confidence:** {result.confidence}\n\n")
            f.write("---\n\n")

            for round_data in result.rounds:
                f.write(f"## Round {round_data.round_number}\n\n")
                f.write(f"**Timestamp:** {round_data.timestamp}\n\n")

                f.write("### Challenges\n\n")
                if round_data.challenges:
                    for c in round_data.challenges:
                        if isinstance(c, dict):
                            f.write(f"- **[{c.get('challenger', 'Unknown')}]** ({c.get('severity', 'N/A')}): {c.get('issue', 'N/A')}\n")
                else:
                    f.write("No challenges raised.\n")

                f.write("\n### Responses\n\n")
                if round_data.responses:
                    for r in round_data.responses:
                        if isinstance(r, dict):
                            status = "Addressed" if r.get('addressed') else "Not Addressed"
                            f.write(f"- **{status}**: {r.get('explanation', 'N/A')}\n")
                else:
                    f.write("No responses needed.\n")

                f.write(f"\n**Round Outcome:** {round_data.outcome}\n\n")
                f.write("---\n\n")


def create_logic_checker(rules: List[Dict]) -> Callable[[Dict], List[Challenge]]:
    """
    Factory function to create a SUP-A logic checker.

    Args:
        rules: List of logic rules to check against

    Returns:
        Function that checks analysis against logic rules
    """
    def check_logic(analysis: Dict) -> List[Challenge]:
        challenges = []

        for rule in rules:
            field = rule.get("field")
            condition = rule.get("condition")
            message = rule.get("message")
            severity = rule.get("severity", "medium")

            value = analysis.get(field)

            if condition == "required" and value is None:
                challenges.append(Challenge(
                    challenger="SUP-A",
                    challenge_type="logic",
                    issue=message or f"Missing required field: {field}",
                    severity=severity,
                    suggested_action=f"Provide value for {field}"
                ))

            elif condition == "consistency" and callable(rule.get("check")):
                if not rule["check"](analysis):
                    challenges.append(Challenge(
                        challenger="SUP-A",
                        challenge_type="logic",
                        issue=message or f"Consistency check failed for {field}",
                        severity=severity,
                        suggested_action=rule.get("action", "Review and correct")
                    ))

        return challenges

    return check_logic


def create_data_validator(validations: List[Dict]) -> Callable[[Dict], List[Challenge]]:
    """
    Factory function to create a SUP-B data validator.

    Args:
        validations: List of data validation rules

    Returns:
        Function that validates data in analysis
    """
    def validate_data(analysis: Dict) -> List[Challenge]:
        challenges = []

        for validation in validations:
            field = validation.get("field")
            vtype = validation.get("type")
            message = validation.get("message")
            severity = validation.get("severity", "medium")

            value = analysis.get(field)

            if vtype == "range" and value is not None:
                min_val = validation.get("min")
                max_val = validation.get("max")
                if min_val is not None and value < min_val:
                    challenges.append(Challenge(
                        challenger="SUP-B",
                        challenge_type="data",
                        issue=message or f"{field} below minimum ({value} < {min_val})",
                        severity=severity,
                        suggested_action=f"Verify {field} value"
                    ))
                if max_val is not None and value > max_val:
                    challenges.append(Challenge(
                        challenger="SUP-B",
                        challenge_type="data",
                        issue=message or f"{field} above maximum ({value} > {max_val})",
                        severity=severity,
                        suggested_action=f"Verify {field} value"
                    ))

            elif vtype == "source" and validation.get("required_sources"):
                sources = analysis.get("sources", [])
                required = validation["required_sources"]
                missing = [s for s in required if s not in sources]
                if missing:
                    challenges.append(Challenge(
                        challenger="SUP-B",
                        challenge_type="data",
                        issue=f"Missing data sources: {missing}",
                        severity=severity,
                        suggested_action="Add missing data sources"
                    ))

        return challenges

    return validate_data
