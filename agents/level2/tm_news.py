"""
TM-NEWS: News & Policy Task Manager
Analyzes recent news, policy changes, weather impacts, market events
Uses real data from Google News RSS and other sources
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .base import TaskManager
from core.data_fetch import DataFetcher


class NewsManager(TaskManager):
    """
    News & Policy Analysis Task Manager
    Scope: Policy changes, weather, trade developments, market-moving events
    """

    MODULE_NAME = "tm_news"

    # Key themes to monitor for commodities
    NEWS_THEMES = {
        "aluminum": {
            "policy_keywords": ["tariff", "sanction", "carbon", "policy", "regulation"],
            "supply_keywords": ["smelter", "production", "power", "curtailment", "alumina"],
            "demand_keywords": ["EV", "construction", "packaging", "automotive", "demand"],
            "key_regions": ["China", "Europe", "USA", "Russia"],
        },
        "copper": {
            "policy_keywords": ["tariff", "sanction", "green", "policy", "regulation"],
            "supply_keywords": ["mine", "strike", "production", "supply", "Chile", "Peru"],
            "demand_keywords": ["EV", "construction", "renewable", "grid", "demand"],
            "key_regions": ["China", "Chile", "Peru", "DRC", "USA"],
        },
        "cotton": {
            "policy_keywords": ["tariff", "subsidy", "policy", "ban", "regulation"],
            "supply_keywords": ["crop", "harvest", "weather", "drought", "production"],
            "demand_keywords": ["textile", "fashion", "demand", "export", "import"],
            "key_regions": ["USA", "China", "India", "Brazil", "Pakistan"],
        },
        "sugar": {
            "policy_keywords": ["ethanol", "policy", "subsidy", "quota", "regulation"],
            "supply_keywords": ["crop", "harvest", "weather", "Brazil", "production"],
            "demand_keywords": ["consumption", "demand", "import", "export"],
            "key_regions": ["Brazil", "India", "Thailand", "EU"],
        },
    }

    def fetch_data(self) -> Dict:
        """Fetch news from multiple internet sources"""
        commodity_key = self.commodity.lower().replace(" ", "_")
        themes = self.NEWS_THEMES.get(commodity_key, self._get_default_themes())

        # Use DataFetcher to get real news data
        fetcher = DataFetcher(self.commodity, force_refresh=self.force_refresh)
        news_data = fetcher.fetch_news()

        return {
            "commodity": self.commodity,
            "fetched_at": datetime.now().isoformat(),
            "themes": themes,
            "news_data": news_data,
            "news_items": news_data.get("items", []),
            "sources_checked": news_data.get("sources_fetched", []),
            "total_news_found": news_data.get("total_found", 0),
        }

    def _get_default_themes(self) -> Dict:
        """Get default themes for unconfigured commodities"""
        return {
            "policy_keywords": ["tariff", "sanction", "policy", "regulation"],
            "supply_keywords": ["production", "supply", "output", "inventory"],
            "demand_keywords": ["demand", "consumption", "import", "export"],
            "key_regions": ["China", "USA", "Europe"],
        }

    def analyze(self, data: Dict) -> Dict:
        """Analyze news impact based on real fetched data"""
        themes = data.get("themes", {})
        news_items = data.get("news_items", [])

        # Categorize and analyze news
        categorized = self._categorize_news(news_items, themes)

        # Analyze each category
        policy_impact = self._analyze_category(categorized.get("policy", []), "Policy & Regulation")
        supply_news = self._analyze_category(categorized.get("supply", []), "Supply Developments")
        demand_news = self._analyze_category(categorized.get("demand", []), "Demand Developments")
        geopolitical = self._analyze_geopolitical(news_items, themes)

        # Weight the impacts
        scores = [
            policy_impact.get("score", 0),
            supply_news.get("score", 0),
            demand_news.get("score", 0),
            geopolitical.get("score", 0),
        ]
        weights = [0.3, 0.3, 0.25, 0.15]
        overall_score = sum(s * w for s, w in zip(scores, weights))

        return {
            "score": round(overall_score, 1),
            "summary": self._generate_summary(overall_score, policy_impact, supply_news, len(news_items)),
            "policy_analysis": policy_impact,
            "supply_news": supply_news,
            "demand_news": demand_news,
            "geopolitical": geopolitical,
            "key_events": self._identify_key_events(news_items),
            "sources": data.get("sources_checked", []),
            "news_count": len(news_items),
            "recent_headlines": [item.get("title", "") for item in news_items[:5]],
        }

    def _categorize_news(self, news_items: List[Dict], themes: Dict) -> Dict:
        """Categorize news items by theme"""
        categorized = {"policy": [], "supply": [], "demand": [], "other": []}

        policy_kw = themes.get("policy_keywords", [])
        supply_kw = themes.get("supply_keywords", [])
        demand_kw = themes.get("demand_keywords", [])

        for item in news_items:
            title = item.get("title", "").lower()
            desc = item.get("description", "").lower()
            text = title + " " + desc

            matched = False
            if any(kw.lower() in text for kw in policy_kw):
                categorized["policy"].append(item)
                matched = True
            if any(kw.lower() in text for kw in supply_kw):
                categorized["supply"].append(item)
                matched = True
            if any(kw.lower() in text for kw in demand_kw):
                categorized["demand"].append(item)
                matched = True
            if not matched:
                categorized["other"].append(item)

        return categorized

    def _analyze_category(self, items: List[Dict], category_name: str) -> Dict:
        """Analyze a category of news items"""
        if not items:
            return {
                "category": category_name,
                "count": 0,
                "score": 0,
                "rationale": f"No significant {category_name.lower()} news detected",
                "severity": "low",
                "headlines": [],
            }

        # Sentiment scoring based on keywords
        bullish_words = ["rise", "surge", "increase", "strong", "shortage", "rally", "gain", "boost", "demand", "growth"]
        bearish_words = ["fall", "drop", "decline", "weak", "surplus", "slump", "loss", "cut", "slowdown", "oversupply"]

        bullish_count = 0
        bearish_count = 0

        for item in items:
            text = (item.get("title", "") + " " + item.get("description", "")).lower()
            bullish_count += sum(1 for word in bullish_words if word in text)
            bearish_count += sum(1 for word in bearish_words if word in text)

        # Calculate score (-2 to +2 range)
        if bullish_count + bearish_count > 0:
            sentiment_ratio = (bullish_count - bearish_count) / (bullish_count + bearish_count)
            score = round(sentiment_ratio * 2, 1)
        else:
            score = 0

        severity = "low"
        if len(items) >= 5:
            severity = "high"
        elif len(items) >= 2:
            severity = "medium"

        return {
            "category": category_name,
            "count": len(items),
            "score": score,
            "rationale": f"{len(items)} news items found; sentiment {'bullish' if score > 0 else 'bearish' if score < 0 else 'neutral'}",
            "severity": severity,
            "headlines": [item.get("title", "")[:100] for item in items[:3]],
            "bullish_signals": bullish_count,
            "bearish_signals": bearish_count,
        }

    def _analyze_geopolitical(self, news_items: List[Dict], themes: Dict) -> Dict:
        """Analyze geopolitical factors"""
        key_regions = themes.get("key_regions", [])
        geopolitical_keywords = ["war", "conflict", "sanction", "trade war", "tension", "crisis", "embargo"]

        geo_items = []
        for item in news_items:
            text = (item.get("title", "") + " " + item.get("description", "")).lower()
            if any(kw in text for kw in geopolitical_keywords):
                geo_items.append(item)

        score = 0
        if len(geo_items) >= 3:
            score = -0.5  # Geopolitical uncertainty typically bearish for risk
        elif len(geo_items) >= 1:
            score = -0.2

        return {
            "category": "Geopolitical",
            "key_regions": key_regions,
            "risk_factors": [item.get("title", "")[:80] for item in geo_items[:3]],
            "count": len(geo_items),
            "score": score,
            "rationale": f"{len(geo_items)} geopolitical risk items detected" if geo_items else "No major geopolitical risks detected",
            "severity": "high" if len(geo_items) >= 3 else "medium" if geo_items else "low",
        }

    def _identify_key_events(self, news_items: List[Dict]) -> List[Dict]:
        """Identify key upcoming or recent events from news"""
        events = []

        # Extract events from news titles
        event_keywords = ["announce", "report", "decision", "meeting", "data", "release", "forecast"]

        for item in news_items[:10]:
            title = item.get("title", "")
            if any(kw in title.lower() for kw in event_keywords):
                events.append({
                    "event": title[:80],
                    "source": item.get("source", "News"),
                    "date": item.get("pub_date", ""),
                })

        return events[:5]

    def _generate_summary(self, score: float, policy: Dict, supply: Dict, news_count: int) -> str:
        """Generate news summary"""
        outlook = "neutral"
        if score <= -0.5:
            outlook = "bearish"
        elif score >= 0.5:
            outlook = "bullish"

        return (
            f"News & Policy outlook: {outlook.upper()} (based on {news_count} news items). "
            f"Policy: {policy.get('rationale', 'N/A')}. "
            f"Supply: {supply.get('rationale', 'N/A')}."
        )

    def get_logic_rules(self) -> List[Dict]:
        """Logic rules for SUP-A"""
        return [
            {
                "field": "score",
                "condition": "required",
                "message": "News score must be provided",
                "severity": "high",
            },
            {
                "field": "policy_analysis",
                "condition": "required",
                "message": "Policy analysis required",
                "severity": "medium",
            },
        ]

    def get_validation_rules(self) -> List[Dict]:
        """Validation rules for SUP-B"""
        return [
            {
                "field": "score",
                "type": "range",
                "min": -5,
                "max": 5,
                "severity": "high",
            },
        ]
