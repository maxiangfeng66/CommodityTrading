"""
TM-TECH: Technical Analysis Task Manager
Analyzes price trends, momentum, support/resistance, key levels
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import TaskManager
from core.data_fetch import DataFetcher, calculate_technical_indicators


class TechnicalManager(TaskManager):
    """
    Technical Analysis Task Manager
    Scope: Trend (60MA), momentum, support/resistance, key triggers
    """

    MODULE_NAME = "tm_tech"

    def fetch_data(self) -> Dict:
        """Fetch price data for technical analysis"""
        fetcher = DataFetcher(self.commodity, force_refresh=self.force_refresh)
        price_data = fetcher.fetch_price_data()

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "price_data": price_data,
            "sources": ["Yahoo Finance"],
        }

    def analyze(self, data: Dict) -> Dict:
        """Perform technical analysis"""
        price_data = data.get("price_data", {})
        prices = price_data.get("prices", [])

        if not prices or len(prices) < 60:
            return {
                "score": 0,
                "summary": "Insufficient price data for technical analysis",
                "error": "Need at least 60 days of price data",
                "sources": data.get("sources", []),
            }

        # Calculate technical indicators
        indicators = calculate_technical_indicators(prices)

        # Analyze trend
        trend_analysis = self._analyze_trend(indicators, prices)

        # Analyze momentum
        momentum_analysis = self._analyze_momentum(indicators)

        # Identify key levels
        key_levels = self._identify_key_levels(prices, indicators)

        # Identify triggers
        triggers = self._identify_triggers(indicators, key_levels)

        # Calculate overall score
        scores = [
            trend_analysis.get("score", 0),
            momentum_analysis.get("score", 0),
            key_levels.get("score", 0),
        ]
        weights = [0.4, 0.35, 0.25]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        # Prepare price data for candlestick chart
        chart_data = self._prepare_chart_data(prices, indicators.get("ma_60"))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, trend_analysis, momentum_analysis),
            "latest_price": indicators.get("latest_close"),
            "indicators": indicators,
            "trend_analysis": trend_analysis,
            "momentum_analysis": momentum_analysis,
            "key_levels": key_levels,
            "triggers": triggers,
            "price_data": chart_data,
            "sources": data.get("sources", []),
        }

    def _analyze_trend(self, indicators: Dict, prices: List) -> Dict:
        """Analyze price trend"""
        latest = indicators.get("latest_close", 0)
        ma_60 = indicators.get("ma_60")
        ma_200 = indicators.get("ma_200")
        above_60ma = indicators.get("above_60ma")

        # Determine trend score
        score = 0
        trend_description = "Neutral"

        if above_60ma is True:
            score = 1
            trend_description = "Bullish - Above 60MA"
        elif above_60ma is False:
            score = -1
            trend_description = "Bearish - Below 60MA"

        # Check MA alignment
        if ma_60 and ma_200:
            if ma_60 > ma_200:
                score += 0.5
                trend_description += " (Golden cross territory)"
            else:
                score -= 0.5
                trend_description += " (Death cross territory)"

        return {
            "current_trend": indicators.get("trend", "neutral"),
            "above_60ma": above_60ma,
            "ma_60": ma_60,
            "ma_200": ma_200,
            "score": score,
            "description": trend_description,
        }

    def _analyze_momentum(self, indicators: Dict) -> Dict:
        """Analyze momentum indicators"""
        rsi = indicators.get("rsi_14")

        score = 0
        momentum_state = "Neutral"

        if rsi:
            if rsi >= 70:
                score = -1  # Overbought - bearish signal
                momentum_state = "Overbought"
            elif rsi <= 30:
                score = 1  # Oversold - bullish signal
                momentum_state = "Oversold"
            elif rsi >= 50:
                score = 0.5
                momentum_state = "Bullish momentum"
            else:
                score = -0.5
                momentum_state = "Bearish momentum"

        return {
            "rsi_14": rsi,
            "rsi_state": momentum_state,
            "score": score,
            "interpretation": f"RSI at {rsi:.1f} - {momentum_state}" if rsi else "RSI not available",
        }

    def _identify_key_levels(self, prices: List, indicators: Dict) -> Dict:
        """Identify key support and resistance levels"""
        closes = [p["close"] for p in prices if p.get("close")]

        if not closes:
            return {"score": 0, "levels": []}

        latest = closes[-1]
        high_52w = indicators.get("high_52w", max(closes))
        low_52w = indicators.get("low_52w", min(closes))
        ma_60 = indicators.get("ma_60")

        # Define key levels
        levels = []

        # 52-week high as resistance
        levels.append({
            "level": high_52w,
            "type": "resistance",
            "description": "52-week high",
            "distance_pct": ((high_52w - latest) / latest) * 100,
        })

        # 52-week low as support
        levels.append({
            "level": low_52w,
            "type": "support",
            "description": "52-week low",
            "distance_pct": ((low_52w - latest) / latest) * 100,
        })

        # 60MA as dynamic level
        if ma_60:
            level_type = "support" if latest > ma_60 else "resistance"
            levels.append({
                "level": ma_60,
                "type": level_type,
                "description": f"60-day MA ({level_type})",
                "distance_pct": ((ma_60 - latest) / latest) * 100,
            })

        # Score based on position relative to levels
        pct_from_high = indicators.get("pct_from_52w_high", 0)
        pct_from_low = indicators.get("pct_from_52w_low", 0)

        score = 0
        if abs(pct_from_high) < 5:
            score = -0.5  # Near resistance
        elif abs(pct_from_low) < 5:
            score = 0.5  # Near support

        return {
            "levels": levels,
            "position": f"{pct_from_high:.1f}% from 52w high, {pct_from_low:.1f}% from 52w low",
            "score": score,
        }

    def _prepare_chart_data(self, prices: List, ma_60: float) -> Dict:
        """Prepare OHLC data for candlestick chart"""
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        ma60_line = []

        for i, p in enumerate(prices):
            dates.append(p.get("date", ""))
            opens.append(p.get("open", 0))
            highs.append(p.get("high", 0))
            lows.append(p.get("low", 0))
            closes.append(p.get("close", 0))

            # Calculate rolling MA for each point if we have enough data
            if i >= 59:
                recent_closes = [prices[j].get("close", 0) for j in range(i - 59, i + 1)]
                ma60_line.append(sum(recent_closes) / 60 if recent_closes else None)
            else:
                ma60_line.append(None)

        return {
            "dates": dates,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "ma60": ma60_line,
        }

    def _identify_triggers(self, indicators: Dict, key_levels: Dict) -> List[Dict]:
        """Identify potential technical triggers"""
        triggers = []

        rsi = indicators.get("rsi_14")
        if rsi:
            if rsi > 65:
                triggers.append({
                    "trigger": "RSI approaching overbought",
                    "direction": "bearish",
                    "probability": "medium",
                })
            elif rsi < 35:
                triggers.append({
                    "trigger": "RSI approaching oversold",
                    "direction": "bullish",
                    "probability": "medium",
                })

        ma_60 = indicators.get("ma_60")
        latest = indicators.get("latest_close")
        if ma_60 and latest:
            distance = abs((latest - ma_60) / ma_60) * 100
            if distance < 2:
                direction = "watch" if latest > ma_60 else "watch"
                triggers.append({
                    "trigger": "Price near 60MA",
                    "direction": "key level test",
                    "probability": "high",
                })

        return triggers

    def _generate_summary(self, score: float, trend: Dict, momentum: Dict) -> str:
        """Generate technical summary"""
        outlook = "neutral"
        if score <= -1:
            outlook = "bearish"
        elif score >= 1:
            outlook = "bullish"

        return (
            f"Technical outlook: {outlook.upper()}. "
            f"Trend: {trend.get('description', 'N/A')}. "
            f"Momentum: {momentum.get('interpretation', 'N/A')}."
        )

    def get_logic_rules(self) -> List[Dict]:
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "Technical score required",
                "severity": "high",
            },
            {
                "field": "indicators",
                "condition": "required",
                "message": "Technical indicators required",
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
