"""
TM-VIEWS: Market Views Task Manager
Analyzes market consensus, analyst forecasts, logic soundness
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .base import TaskManager


class ViewsManager(TaskManager):
    """
    Market Views Analysis Task Manager
    Scope: Consensus positioning, analyst outlook, logic soundness, contrarian signals
    """

    MODULE_NAME = "tm_views"

    def fetch_data(self) -> Dict:
        """Gather market views and analyst opinions"""
        # In production, this would aggregate from:
        # - Bank research reports
        # - Broker forecasts
        # - News sentiment analysis
        # - Social media sentiment

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "analyst_forecasts": self._get_analyst_forecasts(),
            "consensus_view": self._get_consensus_view(),
            "contrarian_indicators": self._get_contrarian_indicators(),
            "sources": [
                "Bank Research Reports",
                "Broker Forecasts",
                "Industry Commentary",
                "Market Sentiment Surveys",
            ],
        }

    def _get_analyst_forecasts(self) -> Dict:
        """Get analyst price forecasts"""
        # Would normally aggregate from multiple sources
        return {
            "average_forecast": "Neutral to slightly bearish",
            "forecast_range": "Wide dispersion",
            "revision_trend": "Recent downgrades",
            "confidence": "Medium",
        }

    def _get_consensus_view(self) -> Dict:
        """Get consensus market view"""
        return {
            "overall_sentiment": "Cautiously bearish",
            "key_themes": [
                "China demand uncertainty",
                "Elevated global stocks",
                "Cost support limited",
            ],
            "bull_arguments": [
                "Green transition demand",
                "Supply discipline improving",
                "Low investor positioning",
            ],
            "bear_arguments": [
                "China property weakness",
                "Global manufacturing slowdown",
                "High inventory levels",
            ],
        }

    def _get_contrarian_indicators(self) -> Dict:
        """Identify contrarian signals"""
        return {
            "sentiment_extreme": False,
            "positioning_extreme": "Monitor COT data",
            "crowded_trade": "Shorts may be building",
            "contrarian_signal": "Weak - consensus not extreme",
        }

    def analyze(self, data: Dict) -> Dict:
        """Analyze market views and assess logic soundness"""
        consensus = data.get("consensus_view", {})
        contrarian = data.get("contrarian_indicators", {})
        forecasts = data.get("analyst_forecasts", {})

        # Assess consensus
        consensus_assessment = self._assess_consensus(consensus)

        # Assess logic soundness
        logic_assessment = self._assess_logic_soundness(consensus)

        # Check for contrarian opportunities
        contrarian_assessment = self._assess_contrarian(contrarian)

        # Weighted score
        scores = [
            consensus_assessment.get("score", 0),
            logic_assessment.get("score", 0),
            contrarian_assessment.get("score", 0),
        ]
        weights = [0.4, 0.35, 0.25]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, consensus_assessment, logic_assessment),
            "consensus_assessment": consensus_assessment,
            "logic_soundness": logic_assessment,
            "contrarian_assessment": contrarian_assessment,
            "analyst_summary": forecasts,
            "sources": data.get("sources", []),
        }

    def _assess_consensus(self, consensus: Dict) -> Dict:
        """Assess the consensus view"""
        sentiment = consensus.get("overall_sentiment", "neutral")

        score_map = {
            "strongly bullish": 2,
            "bullish": 1,
            "cautiously bullish": 0.5,
            "neutral": 0,
            "cautiously bearish": -0.5,
            "bearish": -1,
            "strongly bearish": -2,
        }

        return {
            "consensus_sentiment": sentiment,
            "score": score_map.get(sentiment.lower(), 0),
            "key_themes": consensus.get("key_themes", []),
            "rationale": f"Market consensus is {sentiment}",
        }

    def _assess_logic_soundness(self, consensus: Dict) -> Dict:
        """Assess whether market logic is sound"""
        bull_args = consensus.get("bull_arguments", [])
        bear_args = consensus.get("bear_arguments", [])

        # Evaluate argument quality
        bull_strength = min(len(bull_args), 3)  # Cap at 3
        bear_strength = min(len(bear_args), 3)

        logic_score = 0
        if bear_strength > bull_strength:
            logic_score = -0.5  # Bear case slightly stronger
        elif bull_strength > bear_strength:
            logic_score = 0.5

        return {
            "bull_case_strength": bull_strength,
            "bear_case_strength": bear_strength,
            "logic_sound": True,  # Both sides have valid arguments
            "score": logic_score,
            "assessment": "Market logic appears sound; both bull and bear cases have merit",
            "risk": "Consensus may be overconfident in bear case",
        }

    def _assess_contrarian(self, contrarian: Dict) -> Dict:
        """Assess contrarian opportunities"""
        sentiment_extreme = contrarian.get("sentiment_extreme", False)
        crowded = contrarian.get("crowded_trade", "")

        score = 0
        signal = "Weak"

        if sentiment_extreme:
            score = 1 if "bearish" in str(crowded).lower() else -1
            signal = "Strong contrarian"

        return {
            "contrarian_signal": signal,
            "sentiment_at_extreme": sentiment_extreme,
            "crowded_trade_risk": crowded,
            "score": score,
            "rationale": "No extreme sentiment; limited contrarian opportunity",
        }

    def _generate_summary(self, score: float, consensus: Dict, logic: Dict) -> str:
        """Generate summary"""
        outlook = "neutral"
        if score <= -1:
            outlook = "bearish"
        elif score >= 1:
            outlook = "bullish"

        return (
            f"Market Views: {outlook.upper()}. "
            f"Consensus is {consensus.get('consensus_sentiment', 'mixed')}. "
            f"Logic assessment: {logic.get('assessment', 'N/A')}."
        )

    def get_logic_rules(self) -> List[Dict]:
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "Views score required",
                "severity": "high",
            },
            {
                "field": "logic_soundness",
                "condition": "required",
                "message": "Logic soundness assessment required",
                "severity": "medium",
            },
        ]

    def get_validation_rules(self) -> List[Dict]:
        return [
            {
                "field": "score",
                "type": "range",
                "min": -5,
                "max": 5,
                "severity": "high",
            },
        ]
