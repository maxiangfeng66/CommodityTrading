"""
TM-POS: Positioning Task Manager
Analyzes COT reports, CTA positioning, crowding metrics
Uses real CFTC COT data parsed from public sources
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import TaskManager
from core.data_fetch import DataFetcher


class PositioningManager(TaskManager):
    """
    Positioning Analysis Task Manager
    Scope: COT report, non-commercial positioning, CTA estimates, crowding
    """

    MODULE_NAME = "tm_pos"

    # COT categories
    COT_CATEGORIES = {
        "producer_merchant": "Commercial hedgers",
        "swap_dealer": "Swap dealers",
        "managed_money": "Managed money (specs)",
        "other_reportable": "Other reportables",
    }

    def fetch_data(self) -> Dict:
        """Fetch positioning data from CFTC COT reports"""
        fetcher = DataFetcher(self.commodity, force_refresh=self.force_refresh)
        cot_data = fetcher.fetch_cot_data()
        price_data = fetcher.fetch_price_data()

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "cot_data": cot_data,
            "price_data": price_data,
            "sources": ["CFTC COT Reports", "CTA Positioning Estimates"],
        }

    def analyze(self, data: Dict) -> Dict:
        """Analyze positioning data from real CFTC data"""
        cot_data = data.get("cot_data", {})
        price_data = data.get("price_data", {})

        # Analyze COT positioning
        cot_analysis = self._analyze_cot(cot_data)

        # Analyze spec positioning
        spec_analysis = self._analyze_spec_positioning(cot_data)

        # Estimate CTA positioning based on price trends
        cta_analysis = self._estimate_cta_positioning(price_data)

        # Analyze crowding
        crowding_analysis = self._analyze_crowding(cot_data)

        # Calculate contrarian signals
        contrarian = self._calculate_contrarian_signals(spec_analysis, crowding_analysis)

        # Weighted score
        scores = [
            spec_analysis.get("score", 0),
            cta_analysis.get("score", 0),
            crowding_analysis.get("score", 0),
            contrarian.get("score", 0),
        ]
        weights = [0.35, 0.25, 0.2, 0.2]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, spec_analysis, contrarian),
            "cot_analysis": cot_analysis,
            "spec_positioning": spec_analysis,
            "cta_positioning": cta_analysis,
            "crowding_analysis": crowding_analysis,
            "contrarian_signals": contrarian,
            "sources": data.get("sources", []),
            "data_available": cot_data.get("data_found", False),
        }

    def _analyze_cot(self, cot_data: Dict) -> Dict:
        """Analyze overall COT data"""
        if not cot_data.get("data_found"):
            return {
                "data_source": "CFTC Disaggregated Futures",
                "report_date": "N/A",
                "data_status": "Data not available for this commodity",
                "categories_tracked": list(self.COT_CATEGORIES.values()),
            }

        managed_money = cot_data.get("managed_money", {})
        producer = cot_data.get("producer_merchant", {})
        swap = cot_data.get("swap_dealer", {})

        return {
            "data_source": "CFTC Disaggregated Futures",
            "report_date": cot_data.get("report_date", "Latest"),
            "data_status": "Live data from CFTC",
            "categories_tracked": list(self.COT_CATEGORIES.values()),
            "managed_money_net": managed_money.get("net"),
            "producer_net": producer.get("net"),
            "swap_dealer_net": swap.get("net"),
            "open_interest": cot_data.get("open_interest"),
            "historical_weeks": cot_data.get("historical_count", 0),
        }

    def _analyze_spec_positioning(self, cot_data: Dict) -> Dict:
        """Analyze speculative positioning (managed money)"""
        if not cot_data.get("data_found"):
            return {
                "category": "Managed Money",
                "net_position": "N/A",
                "assessment": "Neutral - data unavailable",
                "score": 0,
            }

        managed_money = cot_data.get("managed_money", {})
        net = managed_money.get("net", 0)
        change = managed_money.get("change", 0)
        percentile = managed_money.get("percentile_52w")

        # Determine assessment based on percentile
        if percentile is not None:
            if percentile >= 80:
                assessment = "Extremely long - contrarian bearish signal"
                score = -0.8
            elif percentile >= 60:
                assessment = "Moderately long - some crowding risk"
                score = -0.3
            elif percentile <= 20:
                assessment = "Extremely short - contrarian bullish signal"
                score = 0.8
            elif percentile <= 40:
                assessment = "Moderately short - potential for covering rally"
                score = 0.3
            else:
                assessment = "Neutral positioning"
                score = 0
        else:
            # No percentile, use net position direction
            if net > 0:
                assessment = f"Net long ({net:,} contracts)"
                score = -0.2  # Slightly negative (crowding risk)
            elif net < 0:
                assessment = f"Net short ({net:,} contracts)"
                score = 0.2  # Slightly positive (covering potential)
            else:
                assessment = "Flat positioning"
                score = 0

        return {
            "category": "Managed Money",
            "net_position": net,
            "position_change": change,
            "percentile_52w": percentile,
            "long_contracts": managed_money.get("long"),
            "short_contracts": managed_money.get("short"),
            "assessment": assessment,
            "score": round(score, 1),
        }

    def _estimate_cta_positioning(self, price_data: Dict) -> Dict:
        """Estimate CTA/trend-follower positioning based on price trends"""
        prices = price_data.get("prices", [])

        if len(prices) < 60:
            return {
                "methodology": "Trend-following model estimate",
                "estimated_position": "Unknown",
                "confidence": "Low",
                "score": 0,
            }

        closes = [p["close"] for p in prices if p.get("close")]

        # Calculate moving averages
        ma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        ma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        ma_200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None

        latest = closes[-1]

        # CTA positioning estimate based on MA alignment
        bullish_signals = 0
        bearish_signals = 0

        if ma_20 and latest > ma_20:
            bullish_signals += 1
        elif ma_20:
            bearish_signals += 1

        if ma_50 and latest > ma_50:
            bullish_signals += 1
        elif ma_50:
            bearish_signals += 1

        if ma_200 and latest > ma_200:
            bullish_signals += 1
        elif ma_200:
            bearish_signals += 1

        if bullish_signals >= 2:
            position = "Long"
            score = 0.3  # Trend followers long = momentum continuation
            confidence = "Medium" if bullish_signals == 2 else "High"
        elif bearish_signals >= 2:
            position = "Short"
            score = -0.3  # Trend followers short = momentum continuation
            confidence = "Medium" if bearish_signals == 2 else "High"
        else:
            position = "Mixed/Flat"
            score = 0
            confidence = "Low"

        return {
            "methodology": "Trend-following model estimate",
            "estimated_position": position,
            "confidence": confidence,
            "factors_considered": [
                f"Price vs 20-day MA: {'Above' if ma_20 and latest > ma_20 else 'Below'}",
                f"Price vs 50-day MA: {'Above' if ma_50 and latest > ma_50 else 'Below'}",
                f"Price vs 200-day MA: {'Above' if ma_200 and latest > ma_200 else 'Below' if ma_200 else 'N/A'}",
            ],
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "score": score,
        }

    def _analyze_crowding(self, cot_data: Dict) -> Dict:
        """Analyze position crowding"""
        if not cot_data.get("data_found"):
            return {
                "crowding_level": "Unknown",
                "risk_assessment": "Unable to assess without COT data",
                "score": 0,
            }

        managed_money = cot_data.get("managed_money", {})
        percentile = managed_money.get("percentile_52w")
        oi = cot_data.get("open_interest", 0)

        if percentile is not None:
            if percentile >= 85 or percentile <= 15:
                crowding = "Extreme"
                risk = "High reversal risk"
                score = -0.5 if percentile >= 85 else 0.5
            elif percentile >= 70 or percentile <= 30:
                crowding = "Elevated"
                risk = "Moderate reversal risk"
                score = -0.2 if percentile >= 70 else 0.2
            else:
                crowding = "Normal"
                risk = "Low reversal risk"
                score = 0
        else:
            crowding = "Unknown"
            risk = "Unable to assess"
            score = 0

        return {
            "crowding_level": crowding,
            "percentile": percentile,
            "open_interest": oi,
            "risk_assessment": risk,
            "score": score,
            "interpretation": f"Managed money positioning at {percentile}th percentile" if percentile else "Percentile data unavailable",
        }

    def _calculate_contrarian_signals(self, spec: Dict, crowding: Dict) -> Dict:
        """Calculate contrarian trading signals"""
        percentile = spec.get("percentile_52w")

        signal_strength = "Weak"
        score = 0
        direction = "None"

        if percentile is not None:
            if percentile >= 90:
                signal_strength = "Strong"
                direction = "Bearish (specs extremely long)"
                score = -1.0
            elif percentile >= 80:
                signal_strength = "Moderate"
                direction = "Bearish (specs very long)"
                score = -0.5
            elif percentile <= 10:
                signal_strength = "Strong"
                direction = "Bullish (specs extremely short)"
                score = 1.0
            elif percentile <= 20:
                signal_strength = "Moderate"
                direction = "Bullish (specs very short)"
                score = 0.5

        return {
            "signal_strength": signal_strength,
            "direction": direction,
            "percentile_trigger": percentile,
            "score": score,
            "rationale": f"Positioning at {percentile}th percentile - {signal_strength.lower()} contrarian signal" if percentile else "Insufficient data for contrarian signals",
        }

    def _generate_summary(self, score: float, spec: Dict, contrarian: Dict) -> str:
        """Generate positioning summary"""
        outlook = "neutral"
        if score <= -0.5:
            outlook = "bearish positioning"
        elif score >= 0.5:
            outlook = "bullish positioning"

        return (
            f"Positioning: {outlook.upper()}. "
            f"Spec assessment: {spec.get('assessment', 'N/A')}. "
            f"Contrarian signal: {contrarian.get('signal_strength', 'N/A')} ({contrarian.get('direction', 'none')})."
        )

    def get_logic_rules(self) -> List[Dict]:
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "Positioning score required",
                "severity": "high",
            },
            {
                "field": "cot_analysis",
                "condition": "required",
                "message": "COT analysis required",
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
