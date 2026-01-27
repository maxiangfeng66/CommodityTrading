"""
TM-STRUCT: Market Structure Task Manager
Analyzes volume, open interest, market attention, liquidity
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import TaskManager
from core.data_fetch import DataFetcher


class StructureManager(TaskManager):
    """
    Market Structure Analysis Task Manager
    Scope: Volume patterns, OI analysis, attention metrics, liquidity
    """

    MODULE_NAME = "tm_struct"

    def fetch_data(self) -> Dict:
        """Fetch market structure data"""
        fetcher = DataFetcher(self.commodity, force_refresh=self.force_refresh)
        price_data = fetcher.fetch_price_data()

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "price_data": price_data,
            "sources": ["Yahoo Finance", "Exchange Data"],
        }

    def analyze(self, data: Dict) -> Dict:
        """Analyze market structure"""
        price_data = data.get("price_data", {})
        prices = price_data.get("prices", [])

        if not prices or len(prices) < 20:
            return {
                "score": 0,
                "summary": "Insufficient data for structure analysis",
                "sources": data.get("sources", []),
            }

        # Analyze volume patterns
        volume_analysis = self._analyze_volume(prices)

        # Analyze market attention (volume trends)
        attention_analysis = self._analyze_attention(prices)

        # Analyze liquidity
        liquidity_analysis = self._analyze_liquidity(prices)

        # Calculate crowding (simplified - would use OI data)
        crowding_analysis = self._analyze_crowding(prices)

        # Weighted score
        scores = [
            volume_analysis.get("score", 0),
            attention_analysis.get("score", 0),
            liquidity_analysis.get("score", 0),
            crowding_analysis.get("score", 0),
        ]
        weights = [0.3, 0.25, 0.25, 0.2]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, volume_analysis, attention_analysis),
            "volume_analysis": volume_analysis,
            "attention_analysis": attention_analysis,
            "liquidity_analysis": liquidity_analysis,
            "crowding_analysis": crowding_analysis,
            "sources": data.get("sources", []),
        }

    def _analyze_volume(self, prices: List) -> Dict:
        """Analyze volume patterns"""
        volumes = [p.get("volume", 0) for p in prices if p.get("volume")]

        if not volumes or len(volumes) < 20:
            return {"score": 0, "status": "Insufficient volume data"}

        # Calculate averages
        avg_5d = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else 0
        avg_20d = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0

        # Volume trend
        volume_ratio = avg_5d / avg_20d if avg_20d > 0 else 1

        score = 0
        trend = "Normal"

        if volume_ratio > 1.5:
            score = 0.5  # High volume - increased attention
            trend = "Elevated"
        elif volume_ratio > 1.2:
            score = 0.25
            trend = "Above average"
        elif volume_ratio < 0.7:
            score = -0.25
            trend = "Below average"

        return {
            "avg_5d_volume": avg_5d,
            "avg_20d_volume": avg_20d,
            "volume_ratio": round(volume_ratio, 2),
            "trend": trend,
            "score": score,
            "interpretation": f"5-day volume {volume_ratio:.1%} of 20-day average",
        }

    def _analyze_attention(self, prices: List) -> Dict:
        """Analyze market attention metrics"""
        # Use volume changes as proxy for attention
        volumes = [p.get("volume", 0) for p in prices[-10:] if p.get("volume")]

        if len(volumes) < 5:
            return {"score": 0, "status": "Insufficient data"}

        # Check for volume spikes
        avg_vol = sum(volumes) / len(volumes)
        max_vol = max(volumes)
        spike_ratio = max_vol / avg_vol if avg_vol > 0 else 1

        attention_level = "Normal"
        score = 0

        if spike_ratio > 2:
            attention_level = "High (volume spike detected)"
            score = 0.5
        elif spike_ratio > 1.5:
            attention_level = "Elevated"
            score = 0.25

        return {
            "attention_level": attention_level,
            "volume_spike_ratio": round(spike_ratio, 2),
            "score": score,
            "interpretation": "Market attention based on volume patterns",
        }

    def _analyze_liquidity(self, prices: List) -> Dict:
        """Analyze market liquidity"""
        # Use volume as proxy for liquidity
        recent_volumes = [p.get("volume", 0) for p in prices[-20:] if p.get("volume")]

        if not recent_volumes:
            return {"score": 0, "status": "No volume data"}

        avg_volume = sum(recent_volumes) / len(recent_volumes)

        # Liquidity assessment (simplified)
        liquidity = "Normal"
        score = 0

        if avg_volume > 0:
            # Higher volume = better liquidity
            liquidity = "Adequate"
            score = 0

        return {
            "average_volume": avg_volume,
            "liquidity_assessment": liquidity,
            "score": score,
            "note": "Liquidity appears adequate for normal trading",
        }

    def _analyze_crowding(self, prices: List) -> Dict:
        """Analyze market crowding (simplified)"""
        # Full analysis would require open interest data from exchanges
        # This provides the framework

        return {
            "oi_available": False,
            "crowding_assessment": "Requires exchange OI data",
            "percentile": "N/A",
            "score": 0,
            "note": "Full crowding analysis requires COT/exchange OI data",
        }

    def _generate_summary(self, score: float, volume: Dict, attention: Dict) -> str:
        """Generate structure summary"""
        outlook = "neutral"
        if score <= -1:
            outlook = "weak structure"
        elif score >= 1:
            outlook = "strong structure"

        return (
            f"Market Structure: {outlook.upper()}. "
            f"Volume trend: {volume.get('trend', 'N/A')}. "
            f"Attention: {attention.get('attention_level', 'N/A')}."
        )

    def get_logic_rules(self) -> List[Dict]:
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "Structure score required",
                "severity": "high",
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
