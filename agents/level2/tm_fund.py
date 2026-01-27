"""
TM-FUND: Fundamentals Task Manager
Analyzes supply/demand balance, production, inventory, seasonal patterns
Uses real data from World Bank, FRED, and other public sources
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import TaskManager
from core.data_fetch import DataFetcher


class FundamentalsManager(TaskManager):
    """
    Fundamentals Analysis Task Manager
    Scope: Supply/demand balance, production forecasts, inventory, seasonal
    """

    MODULE_NAME = "tm_fund"

    # Commodity-specific data and context
    COMMODITY_DATA = {
        "aluminum": {
            "primary_sources": [
                "International Aluminium Institute (IAI)",
                "World Bureau of Metal Statistics",
                "LME Warehouse Data",
                "World Bank Commodity Markets",
            ],
            "global_production_mt": 70_000_000,
            "top_producers": ["China (58%)", "India (6%)", "Russia (5%)", "Canada (4%)"],
            "top_consumers": ["China (58%)", "Europe (12%)", "North America (10%)"],
            "key_cost_drivers": ["Electricity (30-40% of cost)", "Alumina", "Carbon anodes"],
            "seasonal_factors": {
                "Q1": "Weak (post-holiday)",
                "Q2": "Construction pickup",
                "Q3": "Peak demand",
                "Q4": "Pre-holiday restocking",
            },
        },
        "copper": {
            "primary_sources": [
                "International Copper Study Group (ICSG)",
                "World Bureau of Metal Statistics",
                "LME/COMEX Warehouse Data",
                "World Bank Commodity Markets",
            ],
            "global_production_mt": 25_000_000,
            "top_producers": ["Chile (27%)", "Peru (10%)", "China (8%)", "DRC (8%)"],
            "top_consumers": ["China (54%)", "Europe (12%)", "North America (8%)"],
            "key_cost_drivers": ["Mining costs", "Energy", "Labor", "Ore grades"],
            "seasonal_factors": {
                "Q1": "Moderate (China restocking)",
                "Q2": "Construction peak",
                "Q3": "Steady demand",
                "Q4": "Seasonal slowdown",
            },
        },
        "cotton": {
            "primary_sources": [
                "USDA Cotton Reports",
                "International Cotton Advisory Committee (ICAC)",
                "World Bank Commodity Markets",
            ],
            "global_production_mt": 25_000_000,
            "top_producers": ["China (24%)", "India (23%)", "USA (14%)", "Brazil (10%)"],
            "top_consumers": ["China", "India", "Bangladesh", "Vietnam"],
            "key_cost_drivers": ["Weather", "Fertilizer costs", "Labor", "Acreage competition"],
            "seasonal_factors": {
                "Q1": "Southern hemisphere harvest",
                "Q2": "Planting season (Northern)",
                "Q3": "Growing season",
                "Q4": "Northern hemisphere harvest (Sept-Nov)",
            },
        },
        "sugar": {
            "primary_sources": [
                "USDA Sugar Reports",
                "International Sugar Organization (ISO)",
                "World Bank Commodity Markets",
            ],
            "global_production_mt": 180_000_000,
            "top_producers": ["Brazil (20%)", "India (17%)", "EU (8%)", "Thailand (7%)"],
            "key_cost_drivers": ["Weather (Brazil)", "Oil prices (ethanol)", "India policy"],
            "seasonal_factors": {
                "Q1": "Brazil off-season",
                "Q2": "Brazil harvest starts (Apr)",
                "Q3": "Brazil peak harvest",
                "Q4": "India harvest starts (Oct)",
            },
        },
    }

    def fetch_data(self) -> Dict:
        """Fetch fundamental data from public internet sources"""
        commodity_key = self.commodity.lower().replace(" ", "_")
        base_data = self.COMMODITY_DATA.get(commodity_key, self._get_default_data())

        # Use DataFetcher to get real data
        fetcher = DataFetcher(self.commodity, force_refresh=self.force_refresh)
        fundamentals = fetcher.fetch_fundamentals()
        exchange_data = fetcher.fetch_exchange_data()

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "base_data": base_data,
            "world_bank": fundamentals.get("world_bank", {}),
            "economic_indicators": fundamentals.get("economic_indicators", {}),
            "market_context": fundamentals.get("market_context", {}),
            "exchange_data": exchange_data,
            "data_sources": fundamentals.get("data_sources", []),
        }

    def _get_default_data(self) -> Dict:
        """Get default data structure for unconfigured commodities"""
        return {
            "primary_sources": ["World Bank Commodity Markets", "Exchange data"],
            "global_production_mt": "N/A",
            "top_producers": [],
            "top_consumers": [],
            "key_cost_drivers": [],
            "seasonal_factors": {
                "Q1": "Neutral",
                "Q2": "Neutral",
                "Q3": "Neutral",
                "Q4": "Neutral",
            },
        }

    def analyze(self, data: Dict) -> Dict:
        """Analyze fundamentals and produce score"""
        base_data = data.get("base_data", {})
        economic = data.get("economic_indicators", {})

        # Build analysis
        supply_demand = self._analyze_supply_demand(base_data, data.get("market_context", {}))
        inventory = self._analyze_inventory(data)
        seasonal = self._analyze_seasonal(base_data)
        cost_analysis = self._analyze_costs(base_data)
        macro = self._analyze_macro(economic)

        # Calculate overall fundamental score
        scores = [
            supply_demand.get("score", 0),
            inventory.get("score", 0),
            seasonal.get("score", 0),
            cost_analysis.get("score", 0),
            macro.get("score", 0),
        ]
        weights = [0.30, 0.25, 0.15, 0.15, 0.15]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, supply_demand, inventory),
            "supply_demand": supply_demand,
            "inventory_analysis": inventory,
            "seasonal_analysis": seasonal,
            "cost_analysis": cost_analysis,
            "macro_factors": macro,
            "sources": base_data.get("primary_sources", []) + data.get("data_sources", []),
            "data_quality": "high" if data.get("world_bank") else "medium",
        }

    def _analyze_supply_demand(self, base_data: Dict, market_context: Dict) -> Dict:
        """Analyze supply/demand balance"""
        production = base_data.get("global_production_mt", "N/A")
        producers = base_data.get("top_producers", [])
        consumers = base_data.get("top_consumers", [])

        # Get context from market_context
        key_drivers = market_context.get("key_drivers", base_data.get("key_cost_drivers", []))

        # Default neutral assessment
        score = 0
        balance = "balanced"

        # Adjust based on typical market conditions
        if "China" in str(producers) and "China" in str(consumers):
            # China-dominated markets tend to have supply/demand imbalances
            balance = "Slight surplus expected in China-dominated market"
            score = -0.3

        return {
            "global_production": production,
            "top_producers": producers,
            "top_consumers": consumers,
            "key_drivers": key_drivers,
            "demand_outlook": market_context.get("seasonal", "Moderate growth expected"),
            "balance": balance,
            "score": score,
            "rationale": f"Global production {production}; market {balance}",
        }

    def _analyze_inventory(self, data: Dict) -> Dict:
        """Analyze inventory levels from exchange data"""
        exchange = data.get("exchange_data", {})
        volume = exchange.get("volume_analysis", {})

        volume_trend = volume.get("trend", "stable")
        latest_vol = volume.get("latest_volume")
        avg_vol = volume.get("avg_20day")

        # Volume analysis as proxy for activity
        score = 0
        if volume_trend == "increasing":
            score = 0.2  # Increasing activity may indicate demand
        elif volume_trend == "decreasing":
            score = -0.2  # Decreasing activity may indicate weak interest

        return {
            "volume_trend": volume_trend,
            "latest_volume": latest_vol,
            "avg_20day_volume": avg_vol,
            "exchange_data": "Available" if exchange else "Limited",
            "score": score,
            "rationale": f"Volume trend: {volume_trend}; market activity {'elevated' if volume_trend == 'increasing' else 'subdued' if volume_trend == 'decreasing' else 'stable'}",
        }

    def _analyze_seasonal(self, base_data: Dict) -> Dict:
        """Analyze seasonal patterns"""
        seasonal_factors = base_data.get("seasonal_factors", {})
        current_quarter = f"Q{(datetime.now().month - 1) // 3 + 1}"
        current_factor = seasonal_factors.get(current_quarter, "Neutral")

        score_map = {
            "Weak (post-holiday)": -1,
            "Construction pickup": 0.5,
            "Peak demand": 1,
            "Pre-holiday restocking": 0.5,
            "Northern hemisphere harvest (Sept-Nov)": -0.5,
            "Brazil peak harvest": -0.5,
            "Moderate (China restocking)": 0.3,
            "Construction peak": 0.7,
            "Steady demand": 0.2,
            "Seasonal slowdown": -0.3,
            "Neutral": 0,
        }

        score = score_map.get(current_factor, 0)

        return {
            "current_quarter": current_quarter,
            "seasonal_factor": current_factor,
            "historical_pattern": seasonal_factors,
            "score": score,
            "rationale": f"Current quarter ({current_quarter}): {current_factor}",
        }

    def _analyze_costs(self, base_data: Dict) -> Dict:
        """Analyze cost structure"""
        cost_drivers = base_data.get("key_cost_drivers", [])

        return {
            "key_drivers": cost_drivers,
            "cost_outlook": "Production costs provide price floor support",
            "score": 0,  # Neutral - costs provide floor but not catalyst
            "rationale": f"Key cost drivers: {', '.join(cost_drivers[:3]) if cost_drivers else 'N/A'}",
        }

    def _analyze_macro(self, economic: Dict) -> Dict:
        """Analyze macro economic factors"""
        usd = economic.get("usd_index", {})
        usd_latest = usd.get("latest")
        usd_change = usd.get("1m_change_pct")

        score = 0
        assessment = "Neutral"

        if usd_change:
            if usd_change > 2:
                score = -0.5  # Strong USD bearish for commodities
                assessment = "USD strength pressuring commodity prices"
            elif usd_change < -2:
                score = 0.5  # Weak USD bullish for commodities
                assessment = "USD weakness supportive for commodity prices"
            else:
                assessment = "USD stable, neutral impact"

        return {
            "usd_index": usd_latest,
            "usd_change_1m": usd_change,
            "assessment": assessment,
            "score": score,
            "rationale": assessment,
        }

    def _generate_summary(self, score: float, supply_demand: Dict, inventory: Dict) -> str:
        """Generate analysis summary"""
        outlook = "neutral"
        if score <= -0.5:
            outlook = "bearish"
        elif score >= 0.5:
            outlook = "bullish"

        return (
            f"Fundamental outlook: {outlook.upper()}. "
            f"Supply/demand: {supply_demand.get('balance', 'N/A')}. "
            f"Market activity: {inventory.get('rationale', 'N/A')}."
        )

    def get_logic_rules(self) -> List[Dict]:
        """Logic rules for SUP-A to check"""
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "Score must be provided",
                "severity": "high",
            },
            {
                "field": "supply_demand",
                "condition": "required",
                "message": "Supply/demand analysis required",
                "severity": "high",
            },
            {
                "field": "consistency",
                "condition": "consistency",
                "check": lambda a: -5 <= a.get("score", 0) <= 5,
                "message": "Score must be in valid range [-5, 5]",
                "severity": "high",
            },
        ]

    def get_validation_rules(self) -> List[Dict]:
        """Validation rules for SUP-B to check"""
        return [
            {
                "field": "score",
                "type": "range",
                "min": -5,
                "max": 5,
                "severity": "high",
            },
            {
                "field": "sources",
                "type": "source",
                "required_sources": [],
                "severity": "low",
            },
        ]
