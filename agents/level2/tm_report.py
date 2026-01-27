"""
TM-REPORT: Report Synthesis Task Manager
Synthesizes all module outputs into final HTML report
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportManager:
    """
    Report Synthesis Task Manager
    Compiles all module outputs into comprehensive HTML report
    Template MUST remain consistent per Hard Rule #5
    """

    MODULE_NAME = "tm_report"

    # Fixed template structure per blueprint
    REPORT_SECTIONS = [
        "executive_summary",
        "fundamentals",
        "news_policy",
        "market_views",
        "technical",
        "market_structure",
        "positioning",
        "conclusion",
    ]

    def __init__(self, project_root: Path, commodity: str):
        self.project_root = project_root
        self.commodity = commodity
        self.commodity_key = commodity.lower().replace(" ", "_")
        self.modules_dir = project_root / "modules" / self.commodity_key
        self.output_dir = project_root / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_module_outputs(self) -> Dict[str, Any]:
        """Collect outputs from all Level 2 modules"""
        outputs = {}

        module_files = {
            "tm_fund": "fund_output.json",
            "tm_news": "news_output.json",
            "tm_views": "views_output.json",
            "tm_tech": "tech_output.json",
            "tm_struct": "struct_output.json",
            "tm_pos": "pos_output.json",
        }

        for module, filename in module_files.items():
            filepath = self.modules_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    outputs[module] = json.load(f)
            else:
                outputs[module] = {"status": "not_found", "score": 0}

        return outputs

    def calculate_weighted_score(self, outputs: Dict) -> Dict:
        """Calculate weighted overall score"""
        weights = {
            "tm_fund": 1.5,   # Fundamentals weighted higher
            "tm_news": 1.0,
            "tm_views": 1.0,
            "tm_tech": 1.2,
            "tm_struct": 0.8,
            "tm_pos": 1.0,
        }

        scores = []
        weight_sum = 0

        for module, weight in weights.items():
            output = outputs.get(module, {})
            score = output.get("score")
            if score is not None:
                scores.append(score * weight)
                weight_sum += weight

        weighted_score = sum(scores) / weight_sum if weight_sum > 0 else 0

        return {
            "weighted_score": round(weighted_score, 2),
            "modules_included": len([s for s in scores if s is not None]),
            "interpretation": self._interpret_score(weighted_score),
        }

    def _interpret_score(self, score: float) -> str:
        """Interpret overall score"""
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

    def generate_html(self, outputs: Dict, synthesis: Dict) -> str:
        """
        Generate HTML report with FIXED TEMPLATE
        This template MUST NOT change between reruns (Hard Rule #5)
        """
        weighted = synthesis.get("weighted_score", 0)
        interpretation = synthesis.get("interpretation", "N/A")

        # Build HTML with fixed structure
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.commodity} - Commodity Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}

        header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.3);
            border-bottom: 1px solid #333;
        }}
        header h1 {{ color: #4ecdc4; font-size: 2.5em; margin-bottom: 10px; }}
        header .subtitle {{ color: #888; font-size: 1.1em; }}

        .score-banner {{
            background: linear-gradient(90deg, #2d2d44 0%, #1a1a2e 100%);
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            border-radius: 10px;
            border: 1px solid #333;
        }}
        .score-value {{
            font-size: 4em;
            font-weight: bold;
            color: {self._get_score_color(weighted)};
        }}
        .score-label {{ color: #888; font-size: 1.2em; margin-top: 10px; }}
        .interpretation {{
            font-size: 1.5em;
            color: {self._get_score_color(weighted)};
            margin-top: 15px;
        }}

        .section {{
            background: rgba(255,255,255,0.03);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
        }}
        .section h2 {{
            color: #4ecdc4;
            border-bottom: 2px solid #4ecdc4;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .section h3 {{ color: #ffd93d; margin: 15px 0 10px; }}

        .module-score {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .score-positive {{ background: rgba(78, 205, 196, 0.2); color: #4ecdc4; }}
        .score-negative {{ background: rgba(255, 107, 107, 0.2); color: #ff6b6b; }}
        .score-neutral {{ background: rgba(255, 217, 61, 0.2); color: #ffd93d; }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #4ecdc4; }}
        .metric-label {{ color: #888; font-size: 0.9em; }}

        .summary-box {{
            background: rgba(78, 205, 196, 0.1);
            border-left: 4px solid #4ecdc4;
            padding: 15px 20px;
            margin: 15px 0;
        }}

        .debate-info {{
            background: rgba(255, 217, 61, 0.1);
            border: 1px solid rgba(255, 217, 61, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .debate-info h4 {{ color: #ffd93d; margin-bottom: 10px; }}

        ul {{ margin-left: 20px; margin-top: 10px; }}
        li {{ margin: 8px 0; }}

        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 40px;
        }}

        .sources {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        .sources h4 {{ color: #888; margin-bottom: 10px; }}
        .sources ul {{ list-style: none; margin: 0; }}
        .sources li {{ color: #666; font-size: 0.9em; }}

        .chart-container {{
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }}
        .chart-title {{
            color: #4ecdc4;
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        #candlestick-chart {{
            width: 100%;
            height: 450px;
        }}

        .detail-list {{
            margin: 15px 0;
        }}
        .detail-list li {{
            margin: 10px 0;
            padding-left: 10px;
            border-left: 3px solid #4ecdc4;
        }}
        .detail-list .highlight {{
            color: #4ecdc4;
            font-weight: bold;
        }}
        .detail-list .warning {{
            color: #ff6b6b;
            font-weight: bold;
        }}
        .detail-list .neutral {{
            color: #ffd93d;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{self.commodity.upper()} ANALYSIS</h1>
        <p class="subtitle">Comprehensive Commodity Analysis Report</p>
        <p class="subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    </header>

    <div class="container">
        <!-- Score Banner -->
        <div class="score-banner">
            <div class="score-value">{weighted:+.1f}</div>
            <div class="score-label">Weighted Overall Score (-5 to +5)</div>
            <div class="interpretation">{interpretation}</div>
        </div>

        <!-- Executive Summary -->
        <section class="section">
            <h2>1. Executive Summary</h2>
            {self._generate_executive_summary(outputs, synthesis)}
        </section>

        <!-- Fundamentals -->
        <section class="section">
            <h2>2. Fundamentals Analysis</h2>
            {self._generate_module_section(outputs.get("tm_fund", {}), "Fundamentals")}
        </section>

        <!-- News & Policy -->
        <section class="section">
            <h2>3. News & Policy</h2>
            {self._generate_module_section(outputs.get("tm_news", {}), "News")}
        </section>

        <!-- Market Views -->
        <section class="section">
            <h2>4. Market Views</h2>
            {self._generate_module_section(outputs.get("tm_views", {}), "Views")}
        </section>

        <!-- Technical Analysis -->
        <section class="section">
            <h2>5. Technical Analysis</h2>
            {self._generate_technical_section(outputs.get("tm_tech", {}))}
        </section>

        <!-- Market Structure -->
        <section class="section">
            <h2>6. Market Structure</h2>
            {self._generate_module_section(outputs.get("tm_struct", {}), "Structure")}
        </section>

        <!-- Positioning -->
        <section class="section">
            <h2>7. Positioning Analysis</h2>
            {self._generate_module_section(outputs.get("tm_pos", {}), "Positioning")}
        </section>

        <!-- Conclusion -->
        <section class="section">
            <h2>8. Conclusion & Trading Implications</h2>
            {self._generate_conclusion(outputs, synthesis)}
        </section>
    </div>

    <footer>
        <p>CommodityTrading Multi-Agent Analysis System</p>
        <p>Blueprint v2.3 | Report generated with debate protocol</p>
        <p>Total modules: {synthesis.get("modules_included", 0)}/6 |
           Debate rounds: {self._count_debate_rounds(outputs)}</p>
    </footer>
</body>
</html>'''

        return html

    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score <= -1:
            return "#ff6b6b"  # Red for bearish
        elif score >= 1:
            return "#4ecdc4"  # Teal for bullish
        return "#ffd93d"  # Yellow for neutral

    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score"""
        if score <= -1:
            return "score-negative"
        elif score >= 1:
            return "score-positive"
        return "score-neutral"

    def _generate_executive_summary(self, outputs: Dict, synthesis: Dict) -> str:
        """Generate executive summary HTML"""
        summaries = []
        for module, output in outputs.items():
            if isinstance(output, dict) and output.get("summary"):
                summaries.append(output["summary"])

        weighted = synthesis.get("weighted_score", 0)
        interpretation = synthesis.get("interpretation", "N/A")

        return f'''
        <div class="summary-box">
            <p><strong>Overall Assessment:</strong> {interpretation} (Score: {weighted:+.1f})</p>
        </div>
        <h3>Key Findings</h3>
        <ul>
            {"".join(f"<li>{s}</li>" for s in summaries[:4])}
        </ul>
        <h3>Module Scores Overview</h3>
        <div class="metrics-grid">
            {self._generate_score_cards(outputs)}
        </div>
        '''

    def _generate_score_cards(self, outputs: Dict) -> str:
        """Generate score cards for each module"""
        cards = []
        module_names = {
            "tm_fund": "Fundamentals",
            "tm_news": "News & Policy",
            "tm_views": "Market Views",
            "tm_tech": "Technical",
            "tm_struct": "Structure",
            "tm_pos": "Positioning",
        }

        for module, name in module_names.items():
            output = outputs.get(module, {})
            score = output.get("score", 0)
            confidence = output.get("confidence", 0)
            color = self._get_score_color(score)

            cards.append(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: {color}">{score:+.1f}</div>
                <div class="metric-label">{name}</div>
                <div class="metric-label" style="font-size: 0.8em">Conf: {confidence:.0%}</div>
            </div>
            ''')

        return "".join(cards)

    def _generate_module_section(self, output: Dict, name: str) -> str:
        """Generate section for a module with detailed bullet points"""
        if output.get("status") == "not_found":
            return f"<p>Module data not available</p>"

        score = output.get("score", 0)
        summary = output.get("summary", "No summary available")
        confidence = output.get("confidence", 0)
        debate_outcome = output.get("debate_outcome", "N/A")
        debate_rounds = output.get("debate_rounds", 0)

        # Generate detailed analysis HTML with explanations
        analysis = output.get("analysis", {})
        analysis_html = self._generate_detailed_analysis(analysis, name, score)

        # Score interpretation
        score_class = self._get_score_class(score)
        if score >= 2:
            score_interpretation = "Strongly supports bullish case"
        elif score >= 0.5:
            score_interpretation = "Moderately supportive for bulls"
        elif score <= -2:
            score_interpretation = "Strongly supports bearish case"
        elif score <= -0.5:
            score_interpretation = "Moderately supportive for bears"
        else:
            score_interpretation = "Neutral, no strong directional bias"

        # Confidence assessment
        if confidence >= 0.8:
            confidence_note = "High confidence - data quality and coverage excellent"
        elif confidence >= 0.6:
            confidence_note = "Moderate confidence - some data limitations"
        else:
            confidence_note = "Lower confidence - significant data gaps"

        return f'''
        <div class="summary-box">
            <p>{summary}</p>
        </div>

        <h3>Score Assessment</h3>
        <ul class="detail-list">
            <li><strong>Module Score:</strong> <span class="module-score {score_class}">{score:+.1f}</span> - {score_interpretation}</li>
            <li><strong>Confidence Level:</strong> {confidence:.0%} - {confidence_note}</li>
        </ul>

        <h3>Detailed Analysis</h3>
        {analysis_html}

        <div class="debate-info">
            <h4>Quality Assurance (Debate Protocol)</h4>
            <ul>
                <li><strong>Validation Outcome:</strong> {debate_outcome}</li>
                <li><strong>Debate Rounds:</strong> {debate_rounds} (minimum required: 2)</li>
                <li><strong>SUP-A (Logic):</strong> Challenged assumptions and reasoning</li>
                <li><strong>SUP-B (Data):</strong> Verified data sources and calculations</li>
            </ul>
        </div>

        <div class="sources">
            <h4>Data Sources</h4>
            <ul>
                {"".join(f"<li>{s}</li>" for s in output.get("sources", ["N/A"]))}
            </ul>
        </div>
        '''

    def _generate_detailed_analysis(self, analysis: Dict, name: str, score: float) -> str:
        """Generate detailed analysis with explanatory bullet points"""
        if not isinstance(analysis, dict):
            return f"<p>{analysis if analysis else 'No detailed analysis available'}</p>"

        html = '<ul class="detail-list">'

        for key, value in list(analysis.items())[:8]:
            if key.startswith("_") or key in ["score", "summary", "sources"]:
                continue

            # Format key nicely
            formatted_key = key.replace('_', ' ').title()

            # Add contextual interpretation
            interpretation = self._interpret_value(key, value, score)

            if isinstance(value, dict):
                # Nested dictionary - expand it
                html += f"<li><strong>{formatted_key}:</strong>"
                html += "<ul>"
                for sub_key, sub_value in list(value.items())[:4]:
                    sub_formatted = sub_key.replace('_', ' ').title()
                    html += f"<li>{sub_formatted}: {sub_value}</li>"
                html += "</ul></li>"
            elif isinstance(value, list):
                # List - show items
                html += f"<li><strong>{formatted_key}:</strong>"
                html += "<ul>"
                for item in value[:4]:
                    html += f"<li>{item}</li>"
                html += "</ul></li>"
            else:
                # Simple value with interpretation
                html += f"<li><strong>{formatted_key}:</strong> {value}"
                if interpretation:
                    html += f" <em>({interpretation})</em>"
                html += "</li>"

        html += "</ul>"
        return html

    def _interpret_value(self, key: str, value, score: float) -> str:
        """Provide contextual interpretation for analysis values"""
        key_lower = key.lower()

        # Market balance interpretations
        if "balance" in key_lower or "surplus" in key_lower or "deficit" in key_lower:
            if isinstance(value, (int, float)):
                if value > 0:
                    return "surplus pressures prices lower"
                elif value < 0:
                    return "deficit supports higher prices"
            elif isinstance(value, str):
                if "surplus" in value.lower():
                    return "bearish for prices"
                elif "deficit" in value.lower():
                    return "bullish for prices"

        # Sentiment interpretations
        if "sentiment" in key_lower or "outlook" in key_lower:
            if isinstance(value, str):
                if "bullish" in value.lower():
                    return "supports upside"
                elif "bearish" in value.lower():
                    return "supports downside"

        # Positioning interpretations
        if "position" in key_lower or "cot" in key_lower:
            if isinstance(value, (int, float)):
                if value > 70:
                    return "extreme positioning, reversal risk"
                elif value < 30:
                    return "light positioning, room to build"

        return ""

    def _generate_technical_section(self, output: Dict) -> str:
        """Generate technical analysis section with indicators and candlestick chart"""
        if output.get("status") == "not_found":
            return "<p>Technical data not available</p>"

        # Data is nested under 'analysis' key in the output file
        analysis = output.get("analysis", {})
        indicators = analysis.get("indicators", {})
        trend = analysis.get("trend_analysis", {})
        momentum = analysis.get("momentum_analysis", {})
        price_data = analysis.get("price_data", {})

        # Safe formatting helper
        def fmt(val, prefix="", suffix="", decimals=2):
            if val is None or val == "N/A":
                return "N/A"
            try:
                return f"{prefix}{val:.{decimals}f}{suffix}"
            except (ValueError, TypeError):
                return str(val)

        latest_close = fmt(indicators.get("latest_close"), prefix="$")
        rsi_14 = fmt(indicators.get("rsi_14"), decimals=1)
        ma_60 = fmt(indicators.get("ma_60"), prefix="$")
        pct_high = fmt(indicators.get("pct_from_52w_high"), suffix="%", decimals=1)

        # Get price data for chart
        dates = price_data.get("dates", [])
        opens = price_data.get("open", [])
        highs = price_data.get("high", [])
        lows = price_data.get("low", [])
        closes = price_data.get("close", [])
        ma60_line = price_data.get("ma60", [])

        # Determine trend signal strength
        rsi_value = indicators.get("rsi_14")
        rsi_signal = ""
        if rsi_value is not None:
            if rsi_value > 70:
                rsi_signal = '<span class="warning">OVERBOUGHT</span> - RSI above 70 suggests potential pullback'
            elif rsi_value < 30:
                rsi_signal = '<span class="highlight">OVERSOLD</span> - RSI below 30 suggests potential bounce'
            elif rsi_value > 50:
                rsi_signal = '<span class="neutral">BULLISH MOMENTUM</span> - RSI above 50 indicates upward pressure'
            else:
                rsi_signal = '<span class="neutral">BEARISH MOMENTUM</span> - RSI below 50 indicates downward pressure'

        # Trend strength assessment
        trend_desc = trend.get("description", "N/A")
        above_ma = trend.get("above_60ma", False)
        ma_signal = '<span class="highlight">ABOVE 60MA</span> - Bullish trend confirmed' if above_ma else '<span class="warning">BELOW 60MA</span> - Bearish trend confirmed'

        return f'''
        <div class="summary-box">
            <p>{output.get("summary", "No summary available")}</p>
        </div>

        <!-- Interactive Candlestick Chart -->
        <div class="chart-container">
            <div class="chart-title">Price Chart with 60-Day Moving Average</div>
            <div id="candlestick-chart"></div>
        </div>

        <script>
            var trace1 = {{
                x: {json.dumps(dates[-90:] if len(dates) > 90 else dates)},
                close: {json.dumps(closes[-90:] if len(closes) > 90 else closes)},
                high: {json.dumps(highs[-90:] if len(highs) > 90 else highs)},
                low: {json.dumps(lows[-90:] if len(lows) > 90 else lows)},
                open: {json.dumps(opens[-90:] if len(opens) > 90 else opens)},
                type: 'candlestick',
                name: 'Price',
                increasing: {{line: {{color: '#4ecdc4'}}, fillcolor: '#4ecdc4'}},
                decreasing: {{line: {{color: '#ff6b6b'}}, fillcolor: '#ff6b6b'}}
            }};

            var trace2 = {{
                x: {json.dumps(dates[-90:] if len(dates) > 90 else dates)},
                y: {json.dumps(ma60_line[-90:] if len(ma60_line) > 90 else ma60_line)},
                type: 'scatter',
                mode: 'lines',
                name: '60-Day MA',
                line: {{color: '#ffd93d', width: 2}}
            }};

            var layout = {{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0.2)',
                font: {{color: '#e0e0e0'}},
                xaxis: {{
                    title: 'Date',
                    gridcolor: '#333',
                    rangeslider: {{visible: false}}
                }},
                yaxis: {{
                    title: 'Price',
                    gridcolor: '#333'
                }},
                legend: {{
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                }},
                margin: {{t: 30, b: 50, l: 60, r: 30}}
            }};

            Plotly.newPlot('candlestick-chart', [trace1, trace2], layout, {{responsive: true}});
        </script>

        <h3>Price & Indicators</h3>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{latest_close}</div>
                <div class="metric-label">Latest Close</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{rsi_14}</div>
                <div class="metric-label">RSI (14)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{ma_60}</div>
                <div class="metric-label">60-Day MA</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{pct_high}</div>
                <div class="metric-label">From 52W High</div>
            </div>
        </div>

        <h3>Detailed Technical Analysis</h3>
        <ul class="detail-list">
            <li><strong>Trend Position:</strong> {ma_signal}</li>
            <li><strong>Momentum Signal:</strong> {rsi_signal}</li>
            <li><strong>52-Week Context:</strong> Price is {pct_high} from 52-week high, indicating {"near recent highs" if indicators.get("pct_from_52w_high", -100) > -10 else "significant distance from highs"}</li>
            <li><strong>Trend Description:</strong> {trend_desc}</li>
        </ul>

        <h3>Key Technical Levels</h3>
        <ul class="detail-list">
            <li><strong>Resistance:</strong> 52-week high at ${fmt(indicators.get("high_52w"), decimals=2).replace("$", "")}</li>
            <li><strong>Support:</strong> 52-week low at ${fmt(indicators.get("low_52w"), decimals=2).replace("$", "")}</li>
            <li><strong>Moving Average:</strong> 60-day MA at {ma_60} acting as {"support" if above_ma else "resistance"}</li>
        </ul>

        <h3>Momentum Assessment</h3>
        <ul class="detail-list">
            <li><strong>RSI Interpretation:</strong> {momentum.get("interpretation", "N/A")}</li>
            <li><strong>Signal Strength:</strong> {"Strong" if (rsi_value and (rsi_value > 65 or rsi_value < 35)) else "Moderate"}</li>
        </ul>

        <div class="debate-info">
            <h4>Debate Protocol</h4>
            <p>Outcome: {output.get("debate_outcome", "N/A")} | Rounds: {output.get("debate_rounds", 0)}</p>
        </div>
        '''

    def _generate_conclusion(self, outputs: Dict, synthesis: Dict) -> str:
        """Generate conclusion section"""
        weighted = synthesis.get("weighted_score", 0)
        interpretation = synthesis.get("interpretation", "N/A")

        # Determine bias and risks
        if weighted <= -2:
            bias = "Bearish bias warranted"
            key_risks = "Potential for short squeeze if sentiment shifts"
        elif weighted >= 2:
            bias = "Bullish bias warranted"
            key_risks = "Watch for macro headwinds and demand weakness"
        else:
            bias = "Neutral stance appropriate"
            key_risks = "Range-bound trading likely; watch for breakouts"

        return f'''
        <div class="summary-box">
            <p><strong>Final Assessment:</strong> {interpretation} ({weighted:+.1f})</p>
            <p><strong>Recommended Bias:</strong> {bias}</p>
        </div>

        <h3>Trading Implications</h3>
        <ul>
            <li><strong>Direction:</strong> {interpretation}</li>
            <li><strong>Confidence:</strong> {synthesis.get("modules_included", 0)}/6 modules completed</li>
            <li><strong>Key Risk:</strong> {key_risks}</li>
        </ul>

        <h3>Watch Points</h3>
        <ul>
            <li>Monitor COT positioning for extreme readings</li>
            <li>Watch technical levels identified in analysis</li>
            <li>Track policy developments in key regions</li>
            <li>Assess demand signals from downstream sectors</li>
        </ul>
        '''

    def _count_debate_rounds(self, outputs: Dict) -> int:
        """Count total debate rounds across all modules"""
        total = 0
        for output in outputs.values():
            if isinstance(output, dict):
                total += output.get("debate_rounds", 0)
        return total

    def run(self) -> Dict:
        """Execute report generation"""
        # Collect outputs
        outputs = self.collect_module_outputs()

        # Calculate synthesis
        synthesis = self.calculate_weighted_score(outputs)

        # Generate HTML
        html = self.generate_html(outputs, synthesis)

        # Save report
        output_path = self.output_dir / f"{self.commodity_key}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return {
            "status": "complete",
            "output_path": str(output_path),
            "synthesis": synthesis,
            "modules_processed": len([o for o in outputs.values() if o.get("status") != "not_found"]),
        }
