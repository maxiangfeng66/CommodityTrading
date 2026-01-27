"""
Data Fetching Module
Fetches commodity data from multiple public internet sources
Enhanced version with real data parsing
"""

import json
import os
import re
import csv
import io
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote, urlencode
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CACHE = PROJECT_ROOT / "data" / "cache"

# Disable SSL verification for some sources
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


class DataFetcher:
    """Fetches commodity data from multiple public internet sources"""

    # Commodity mappings for different sources
    COMMODITY_SYMBOLS = {
        "aluminum": {
            "yahoo": "ALI=F",
            "name": "Aluminum",
            "exchange": "LME/COMEX",
            "unit": "USD/MT",
            "cftc_code": "085692",
            "cftc_name": "ALUMINUM",
            "world_bank_code": "ALUMINUM",
            "news_keywords": ["aluminum", "aluminium", "LME aluminum", "aluminum futures"],
        },
        "copper": {
            "yahoo": "HG=F",
            "name": "Copper",
            "exchange": "COMEX",
            "unit": "USD/lb",
            "cftc_code": "085692",
            "cftc_name": "COPPER",
            "world_bank_code": "COPPER",
            "news_keywords": ["copper", "COMEX copper", "copper futures", "copper price"],
        },
        "cotton": {
            "yahoo": "CT=F",
            "name": "Cotton No.2",
            "exchange": "ICE",
            "unit": "USc/lb",
            "cftc_code": "033661",
            "cftc_name": "COTTON NO. 2",
            "world_bank_code": "COTTON_A_INDX",
            "news_keywords": ["cotton", "ICE cotton", "cotton futures", "cotton price"],
        },
        "sugar": {
            "yahoo": "SB=F",
            "name": "Sugar No.11",
            "exchange": "ICE",
            "unit": "USc/lb",
            "cftc_code": "080732",
            "cftc_name": "SUGAR NO. 11",
            "world_bank_code": "SUGAR_WLD",
            "news_keywords": ["sugar", "ICE sugar", "sugar futures", "sugar price"],
        },
        "silver": {
            "yahoo": "SI=F",
            "name": "Silver",
            "exchange": "COMEX",
            "unit": "USD/oz",
            "cftc_code": "084691",
            "cftc_name": "SILVER",
            "world_bank_code": "SILVER",
            "news_keywords": ["silver", "COMEX silver", "silver futures", "silver price"],
        },
        "gold": {
            "yahoo": "GC=F",
            "name": "Gold",
            "exchange": "COMEX",
            "unit": "USD/oz",
            "cftc_code": "088691",
            "cftc_name": "GOLD",
            "world_bank_code": "GOLD",
            "news_keywords": ["gold", "COMEX gold", "gold futures", "gold price"],
        },
        "crude_oil": {
            "yahoo": "CL=F",
            "name": "WTI Crude Oil",
            "exchange": "NYMEX",
            "unit": "USD/bbl",
            "cftc_code": "067651",
            "cftc_name": "CRUDE OIL, LIGHT SWEET",
            "world_bank_code": "CRUDE_WTI",
            "news_keywords": ["crude oil", "WTI", "oil futures", "oil price"],
        },
        "natural_gas": {
            "yahoo": "NG=F",
            "name": "Natural Gas",
            "exchange": "NYMEX",
            "unit": "USD/MMBtu",
            "cftc_code": "023651",
            "cftc_name": "NATURAL GAS",
            "world_bank_code": "NGAS_US",
            "news_keywords": ["natural gas", "nat gas", "gas futures", "henry hub"],
        },
        "corn": {
            "yahoo": "ZC=F",
            "name": "Corn",
            "exchange": "CBOT",
            "unit": "USc/bu",
            "cftc_code": "002602",
            "cftc_name": "CORN",
            "world_bank_code": "CORN",
            "news_keywords": ["corn", "corn futures", "CBOT corn", "corn price"],
        },
        "wheat": {
            "yahoo": "ZW=F",
            "name": "Wheat",
            "exchange": "CBOT",
            "unit": "USc/bu",
            "cftc_code": "001602",
            "cftc_name": "WHEAT",
            "world_bank_code": "WHEAT_US_HRW",
            "news_keywords": ["wheat", "wheat futures", "CBOT wheat", "wheat price"],
        },
        "soybeans": {
            "yahoo": "ZS=F",
            "name": "Soybeans",
            "exchange": "CBOT",
            "unit": "USc/bu",
            "cftc_code": "005602",
            "cftc_name": "SOYBEANS",
            "world_bank_code": "SOYBEAN",
            "news_keywords": ["soybeans", "soybean futures", "CBOT soybeans"],
        },
        "iron_ore": {
            "yahoo": None,
            "name": "Iron Ore",
            "exchange": "SGX/DCE",
            "unit": "USD/MT",
            "cftc_code": None,
            "cftc_name": None,
            "world_bank_code": "IRON_ORE",
            "news_keywords": ["iron ore", "iron ore price", "DCE iron ore"],
        },
    }

    def __init__(self, commodity: str, force_refresh: bool = False):
        self.commodity = commodity.lower().replace(" ", "_")
        self.config = self.COMMODITY_SYMBOLS.get(self.commodity, {})
        self.cache_dir = DATA_CACHE
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.force_refresh = force_refresh

    def _get_cache_path(self, source: str) -> Path:
        """Get cache file path for a source"""
        date_str = datetime.now().strftime("%Y%m%d")
        return self.cache_dir / f"{self.commodity}_{source}_{date_str}.json"

    def _load_cache(self, source: str) -> Optional[Dict]:
        """Load cached data if exists and fresh"""
        cache_path = self._get_cache_path(source)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def _save_cache(self, source: str, data: Dict):
        """Save data to cache"""
        cache_path = self._get_cache_path(source)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def _fetch_url(self, url: str, headers: Dict = None, timeout: int = 30) -> Optional[str]:
        """Fetch URL content with error handling"""
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            req.add_header('Accept-Language', 'en-US,en;q=0.5')
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            with urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
                return response.read().decode('utf-8', errors='ignore')
        except (URLError, HTTPError) as e:
            print(f"[DataFetcher] Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"[DataFetcher] Unexpected error fetching {url}: {e}")
            return None

    def fetch_price_data(self) -> Dict:
        """Fetch price data from Yahoo Finance"""
        if not self.force_refresh:
            cached = self._load_cache("price")
            if cached:
                return cached

        symbol = self.config.get("yahoo")
        if not symbol:
            return {"error": f"No Yahoo symbol for {self.commodity}"}

        end_ts = int(datetime.now().timestamp())
        start_ts = int((datetime.now() - timedelta(days=365)).timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"

        content = self._fetch_url(url)
        if not content:
            return {"error": "Failed to fetch price data"}

        try:
            data = json.loads(content)
            result = data.get("chart", {}).get("result", [{}])[0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]

            prices = []
            for i, ts in enumerate(timestamps):
                if quotes.get("close") and i < len(quotes["close"]) and quotes["close"][i]:
                    prices.append({
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        "open": quotes.get("open", [None])[i],
                        "high": quotes.get("high", [None])[i],
                        "low": quotes.get("low", [None])[i],
                        "close": quotes["close"][i],
                        "volume": quotes.get("volume", [None])[i],
                    })

            price_data = {
                "symbol": symbol,
                "commodity": self.config.get("name", self.commodity),
                "exchange": self.config.get("exchange"),
                "unit": self.config.get("unit"),
                "fetched_at": datetime.now().isoformat(),
                "prices": prices[-252:],
                "latest": prices[-1] if prices else None,
            }

            self._save_cache("price", price_data)
            return price_data

        except Exception as e:
            return {"error": f"Failed to parse price data: {e}"}

    def fetch_cot_data(self) -> Dict:
        """Fetch and parse COT (Commitment of Traders) data from CFTC"""
        if not self.force_refresh:
            cached = self._load_cache("cot")
            if cached:
                return cached

        cftc_name = self.config.get("cftc_name")
        if not cftc_name:
            return {"error": f"No CFTC name for {self.commodity}", "source": "CFTC"}

        # CFTC Disaggregated Futures-Only Combined Report
        # Current year file
        url = "https://www.cftc.gov/dea/newcot/f_disagg.txt"

        print(f"[DataFetcher] Fetching CFTC COT data for {cftc_name}...")
        content = self._fetch_url(url, timeout=60)

        if not content:
            # Try the legacy format
            url = "https://www.cftc.gov/dea/newcot/deafut.txt"
            content = self._fetch_url(url, timeout=60)

        if not content:
            return {"error": "Failed to fetch COT data", "source": "CFTC"}

        try:
            # Parse the CSV data
            lines = content.strip().split('\n')
            if len(lines) < 2:
                return {"error": "No COT data found", "source": "CFTC"}

            # The file is comma-separated with quoted fields
            reader = csv.reader(io.StringIO(content))
            headers = next(reader)

            # Find relevant columns
            name_col = next((i for i, h in enumerate(headers) if 'Market_and_Exchange_Names' in h or 'Market and Exchange Names' in h), 0)

            # Find this commodity's data
            commodity_rows = []
            for row in reader:
                if len(row) > name_col:
                    market_name = row[name_col].upper()
                    if cftc_name.upper() in market_name:
                        commodity_rows.append(row)

            if not commodity_rows:
                return {
                    "source": "CFTC",
                    "fetched_at": datetime.now().isoformat(),
                    "commodity": self.config.get("name"),
                    "cftc_name": cftc_name,
                    "data_found": False,
                    "note": f"No data found for {cftc_name} in COT report",
                }

            # Get the most recent row (last in the list)
            latest_row = commodity_rows[-1] if commodity_rows else None

            # Parse key columns - column indices vary by report format
            # Try to find managed money and producer columns
            col_map = {h.strip(): i for i, h in enumerate(headers)}

            def safe_get(row, key_patterns, default=None):
                """Safely get value from row using multiple possible column names"""
                for pattern in key_patterns:
                    for col_name, idx in col_map.items():
                        if pattern.lower() in col_name.lower() and idx < len(row):
                            try:
                                val = row[idx].strip().replace(',', '')
                                return int(float(val)) if val and val != '-' else default
                            except:
                                pass
                return default

            # Extract positioning data
            if latest_row:
                report_date = safe_get(latest_row, ['Report_Date', 'As_of_Date'], 'Unknown')

                # Managed Money (specs)
                mm_long = safe_get(latest_row, ['M_Money_Positions_Long', 'Managed_Money_Long'], 0)
                mm_short = safe_get(latest_row, ['M_Money_Positions_Short', 'Managed_Money_Short'], 0)
                mm_net = (mm_long or 0) - (mm_short or 0)

                # Producer/Merchant (commercials)
                prod_long = safe_get(latest_row, ['Prod_Merc_Positions_Long', 'Producer_Long'], 0)
                prod_short = safe_get(latest_row, ['Prod_Merc_Positions_Short', 'Producer_Short'], 0)
                prod_net = (prod_long or 0) - (prod_short or 0)

                # Swap Dealer
                swap_long = safe_get(latest_row, ['Swap_Positions_Long', 'Swap_Long'], 0)
                swap_short = safe_get(latest_row, ['Swap_Positions_Short', 'Swap_Short'], 0)
                swap_net = (swap_long or 0) - (swap_short or 0)

                # Open Interest
                oi = safe_get(latest_row, ['Open_Interest', 'OI_All'], 0)

                # Change from prior week
                mm_change = safe_get(latest_row, ['Change_M_Money_Long', 'CHG_M_Money_Long'], 0)

                cot_data = {
                    "source": "CFTC",
                    "fetched_at": datetime.now().isoformat(),
                    "commodity": self.config.get("name"),
                    "cftc_name": cftc_name,
                    "report_date": str(report_date) if report_date else "Latest",
                    "data_found": True,
                    "managed_money": {
                        "long": mm_long,
                        "short": mm_short,
                        "net": mm_net,
                        "change": mm_change,
                    },
                    "producer_merchant": {
                        "long": prod_long,
                        "short": prod_short,
                        "net": prod_net,
                    },
                    "swap_dealer": {
                        "long": swap_long,
                        "short": swap_short,
                        "net": swap_net,
                    },
                    "open_interest": oi,
                    "historical_count": len(commodity_rows),
                }

                # Calculate percentile if we have historical data
                if len(commodity_rows) >= 52:
                    historical_nets = []
                    for row in commodity_rows[-52:]:
                        mm_l = safe_get(row, ['M_Money_Positions_Long', 'Managed_Money_Long'], 0)
                        mm_s = safe_get(row, ['M_Money_Positions_Short', 'Managed_Money_Short'], 0)
                        if mm_l is not None and mm_s is not None:
                            historical_nets.append((mm_l or 0) - (mm_s or 0))

                    if historical_nets and mm_net is not None:
                        sorted_nets = sorted(historical_nets)
                        percentile = (sum(1 for x in sorted_nets if x < mm_net) / len(sorted_nets)) * 100
                        cot_data["managed_money"]["percentile_52w"] = round(percentile, 1)

                self._save_cache("cot", cot_data)
                return cot_data

        except Exception as e:
            print(f"[DataFetcher] Error parsing COT data: {e}")
            return {"error": f"Failed to parse COT data: {e}", "source": "CFTC"}

        return {"error": "No matching COT data found", "source": "CFTC"}

    def fetch_news(self) -> Dict:
        """Fetch recent news from Google News RSS"""
        if not self.force_refresh:
            cached = self._load_cache("news")
            if cached:
                return cached

        commodity_name = self.config.get("name", self.commodity)
        keywords = self.config.get("news_keywords", [commodity_name])

        news_items = []
        sources_fetched = []

        # Fetch from Google News RSS for each keyword
        for keyword in keywords[:3]:  # Limit to first 3 keywords for efficiency
            encoded_keyword = quote(keyword)
            url = f"https://news.google.com/rss/search?q={encoded_keyword}+commodity&hl=en-US&gl=US&ceid=US:en"

            print(f"[DataFetcher] Fetching news for: {keyword}")
            content = self._fetch_url(url, timeout=15)

            if content:
                sources_fetched.append(f"Google News ({keyword})")
                # Parse RSS XML
                items = self._parse_rss(content, keyword)
                news_items.extend(items)

        # Also try Reuters commodities RSS
        reuters_url = "https://www.reutersagency.com/feed/?best-topics=commodities&post_type=best"
        reuters_content = self._fetch_url(reuters_url, timeout=15)
        if reuters_content:
            sources_fetched.append("Reuters Commodities")
            reuters_items = self._parse_rss(reuters_content, commodity_name, source="Reuters")
            # Filter for commodity-specific news
            for item in reuters_items:
                if any(kw.lower() in item.get("title", "").lower() for kw in keywords):
                    news_items.append(item)

        # Deduplicate and sort by date
        seen_titles = set()
        unique_items = []
        for item in news_items:
            title_key = item.get("title", "")[:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)

        # Sort by date (most recent first)
        unique_items.sort(key=lambda x: x.get("pub_date", ""), reverse=True)

        news_data = {
            "source": "aggregated",
            "fetched_at": datetime.now().isoformat(),
            "commodity": commodity_name,
            "keywords_searched": keywords[:3],
            "sources_fetched": sources_fetched,
            "items": unique_items[:20],  # Top 20 news items
            "total_found": len(unique_items),
        }

        self._save_cache("news", news_data)
        return news_data

    def _parse_rss(self, content: str, filter_keyword: str = None, source: str = "Google News") -> List[Dict]:
        """Parse RSS XML content and extract news items"""
        items = []

        # Simple XML parsing for RSS items
        item_pattern = r'<item>(.*?)</item>'
        title_pattern = r'<title>(.*?)</title>'
        link_pattern = r'<link>(.*?)</link>'
        pubdate_pattern = r'<pubDate>(.*?)</pubDate>'
        desc_pattern = r'<description>(.*?)</description>'

        for match in re.finditer(item_pattern, content, re.DOTALL):
            item_content = match.group(1)

            title_match = re.search(title_pattern, item_content, re.DOTALL)
            link_match = re.search(link_pattern, item_content)
            pubdate_match = re.search(pubdate_pattern, item_content)
            desc_match = re.search(desc_pattern, item_content, re.DOTALL)

            if title_match:
                title = title_match.group(1).strip()
                # Clean up HTML entities and CDATA
                title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
                title = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags

                # Filter by keyword if specified
                if filter_keyword and filter_keyword.lower() not in title.lower():
                    continue

                item = {
                    "title": title[:200],  # Limit title length
                    "source": source,
                    "link": link_match.group(1) if link_match else "",
                    "pub_date": pubdate_match.group(1) if pubdate_match else "",
                }

                if desc_match:
                    desc = desc_match.group(1)[:300]
                    desc = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', desc)
                    desc = re.sub(r'<[^>]+>', '', desc)
                    item["description"] = desc

                items.append(item)

        return items[:15]  # Limit to 15 items per source

    def fetch_fundamentals(self) -> Dict:
        """Fetch fundamental data from World Bank and other sources"""
        if not self.force_refresh:
            cached = self._load_cache("fundamentals")
            if cached:
                return cached

        commodity_name = self.config.get("name", self.commodity)
        wb_code = self.config.get("world_bank_code")

        fund_data = {
            "source": "aggregated",
            "fetched_at": datetime.now().isoformat(),
            "commodity": commodity_name,
            "data_sources": [],
        }

        # Fetch World Bank commodity price data (Pink Sheet)
        if wb_code:
            wb_data = self._fetch_world_bank_prices(wb_code)
            if wb_data and "error" not in wb_data:
                fund_data["world_bank"] = wb_data
                fund_data["data_sources"].append("World Bank Commodity Markets")

        # Fetch FRED data for economic indicators
        fred_data = self._fetch_fred_indicators()
        if fred_data:
            fund_data["economic_indicators"] = fred_data
            fund_data["data_sources"].append("FRED Economic Data")

        # Add commodity-specific context
        fund_data["market_context"] = self._get_commodity_context()

        self._save_cache("fundamentals", fund_data)
        return fund_data

    def _fetch_world_bank_prices(self, commodity_code: str) -> Dict:
        """Fetch commodity prices from World Bank API"""
        # World Bank Commodity Markets (Pink Sheet) API
        # Note: This API provides monthly data
        url = f"https://api.worldbank.org/v2/countries/all/indicators/PCOM.{commodity_code}?format=json&per_page=24&mrnev=24"

        print(f"[DataFetcher] Fetching World Bank data for {commodity_code}...")
        content = self._fetch_url(url, timeout=20)

        if not content:
            # Try alternative World Bank endpoint
            url2 = "https://www.worldbank.org/en/research/commodity-markets"
            return {
                "source": "World Bank",
                "note": "Direct API unavailable, see World Bank Commodity Markets for data",
                "reference_url": url2,
            }

        try:
            data = json.loads(content)
            if len(data) >= 2 and data[1]:
                prices = []
                for entry in data[1]:
                    if entry.get("value"):
                        prices.append({
                            "date": entry.get("date"),
                            "value": entry.get("value"),
                        })

                if prices:
                    return {
                        "source": "World Bank",
                        "commodity_code": commodity_code,
                        "prices": prices[:12],  # Last 12 months
                        "latest": prices[0] if prices else None,
                    }
        except Exception as e:
            print(f"[DataFetcher] Error parsing World Bank data: {e}")

        return {"source": "World Bank", "note": "Data parsing in progress"}

    def _fetch_fred_indicators(self) -> Dict:
        """Fetch economic indicators from FRED (Federal Reserve Economic Data)"""
        # FRED provides free economic data
        indicators = {}

        # USD Index (important for commodities)
        dxy_url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=1d&range=1mo"
        content = self._fetch_url(dxy_url, timeout=15)

        if content:
            try:
                data = json.loads(content)
                result = data.get("chart", {}).get("result", [{}])[0]
                closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
                if closes:
                    valid_closes = [c for c in closes if c]
                    if valid_closes:
                        indicators["usd_index"] = {
                            "latest": round(valid_closes[-1], 2),
                            "1m_change_pct": round(((valid_closes[-1] / valid_closes[0]) - 1) * 100, 2) if valid_closes[0] else None,
                        }
            except:
                pass

        return indicators if indicators else None

    def _get_commodity_context(self) -> Dict:
        """Get commodity-specific fundamental context"""
        contexts = {
            "aluminum": {
                "production": "~70M tonnes/year globally",
                "top_producers": ["China (58%)", "India (6%)", "Russia (5%)", "Canada (4%)"],
                "top_consumers": ["China (58%)", "Europe (12%)", "North America (10%)"],
                "key_drivers": ["Electricity costs (30-40%)", "Alumina supply", "Carbon policies"],
                "seasonal": "Q3 peak demand (construction), Q1 weak (post-holiday)",
            },
            "copper": {
                "production": "~25M tonnes/year globally",
                "top_producers": ["Chile (27%)", "Peru (10%)", "China (8%)", "DRC (8%)"],
                "top_consumers": ["China (54%)", "Europe (12%)", "North America (8%)"],
                "key_drivers": ["Construction demand", "EV/renewables", "Mine supply"],
                "seasonal": "Construction season peaks Q2-Q3",
            },
            "cotton": {
                "production": "~25M tonnes/year globally",
                "top_producers": ["China (24%)", "India (23%)", "USA (14%)", "Brazil (10%)"],
                "top_consumers": ["China", "India", "Bangladesh", "Vietnam"],
                "key_drivers": ["Weather", "Acreage", "Textile demand", "Polyester prices"],
                "seasonal": "Northern hemisphere harvest Sept-Nov",
            },
            "sugar": {
                "production": "~180M tonnes/year globally",
                "top_producers": ["Brazil (20%)", "India (17%)", "EU (8%)", "Thailand (7%)"],
                "key_drivers": ["Brazil crop/weather", "Oil prices (ethanol)", "India policy"],
                "seasonal": "Brazil harvest Apr-Nov, India Oct-Mar",
            },
        }

        return contexts.get(self.commodity, {
            "note": f"Context data for {self.commodity} in development"
        })

    def fetch_exchange_data(self) -> Dict:
        """Fetch exchange-specific data (inventory, open interest)"""
        if not self.force_refresh:
            cached = self._load_cache("exchange")
            if cached:
                return cached

        # Get additional data from Yahoo Finance (volume, OI proxies)
        symbol = self.config.get("yahoo")
        if not symbol:
            return {"error": f"No symbol for {self.commodity}"}

        # Fetch with volume data
        end_ts = int(datetime.now().timestamp())
        start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"

        content = self._fetch_url(url)
        if not content:
            return {"error": "Failed to fetch exchange data"}

        try:
            data = json.loads(content)
            result = data.get("chart", {}).get("result", [{}])[0]
            quotes = result.get("indicators", {}).get("quote", [{}])[0]

            volumes = [v for v in quotes.get("volume", []) if v]

            exchange_data = {
                "symbol": symbol,
                "fetched_at": datetime.now().isoformat(),
                "volume_analysis": {
                    "latest_volume": volumes[-1] if volumes else None,
                    "avg_5day": round(sum(volumes[-5:]) / 5, 0) if len(volumes) >= 5 else None,
                    "avg_20day": round(sum(volumes[-20:]) / 20, 0) if len(volumes) >= 20 else None,
                },
            }

            # Calculate volume trend
            if len(volumes) >= 5:
                recent_avg = sum(volumes[-5:]) / 5
                prior_avg = sum(volumes[-10:-5]) / 5 if len(volumes) >= 10 else recent_avg
                if prior_avg > 0:
                    exchange_data["volume_analysis"]["trend"] = "increasing" if recent_avg > prior_avg * 1.1 else "decreasing" if recent_avg < prior_avg * 0.9 else "stable"

            self._save_cache("exchange", exchange_data)
            return exchange_data

        except Exception as e:
            return {"error": f"Failed to parse exchange data: {e}"}

    def fetch_all(self) -> Dict:
        """Fetch all available data for the commodity in parallel"""
        print(f"[DataFetcher] Fetching all data for {self.commodity}...")

        results = {
            "commodity": self.commodity,
            "config": self.config,
        }

        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.fetch_price_data): "price",
                executor.submit(self.fetch_cot_data): "cot",
                executor.submit(self.fetch_news): "news",
                executor.submit(self.fetch_fundamentals): "fundamentals",
                executor.submit(self.fetch_exchange_data): "exchange",
            }

            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"error": str(e)}

        return results


def calculate_technical_indicators(prices: List[Dict]) -> Dict:
    """Calculate technical indicators from price data"""
    if not prices or len(prices) < 60:
        return {"error": "Insufficient price data"}

    closes = [p["close"] for p in prices if p.get("close")]

    def sma(data, period):
        if len(data) < period:
            return None
        return sum(data[-period:]) / period

    def rsi(data, period=14):
        if len(data) < period + 1:
            return None
        gains = []
        losses = []
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            gains.append(max(0, change))
            losses.append(max(0, -change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    latest_close = closes[-1]
    ma_20 = sma(closes, 20)
    ma_60 = sma(closes, 60)
    ma_200 = sma(closes, 200) if len(closes) >= 200 else None
    rsi_14 = rsi(closes, 14)

    trend = "neutral"
    if ma_60 and latest_close > ma_60:
        trend = "bullish"
    elif ma_60 and latest_close < ma_60:
        trend = "bearish"

    year_closes = closes[-252:] if len(closes) >= 252 else closes
    high_52w = max(year_closes)
    low_52w = min(year_closes)
    pct_from_high = ((latest_close - high_52w) / high_52w) * 100
    pct_from_low = ((latest_close - low_52w) / low_52w) * 100

    return {
        "latest_close": latest_close,
        "ma_20": round(ma_20, 4) if ma_20 else None,
        "ma_60": round(ma_60, 4) if ma_60 else None,
        "ma_200": round(ma_200, 4) if ma_200 else None,
        "rsi_14": round(rsi_14, 2) if rsi_14 else None,
        "trend": trend,
        "above_60ma": latest_close > ma_60 if ma_60 else None,
        "high_52w": round(high_52w, 4),
        "low_52w": round(low_52w, 4),
        "pct_from_52w_high": round(pct_from_high, 2),
        "pct_from_52w_low": round(pct_from_low, 2),
    }


if __name__ == "__main__":
    # Test with copper
    import sys
    commodity = sys.argv[1] if len(sys.argv) > 1 else "copper"
    fetcher = DataFetcher(commodity, force_refresh=True)
    data = fetcher.fetch_all()
    print(json.dumps(data, indent=2, default=str))
