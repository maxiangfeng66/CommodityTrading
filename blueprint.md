# CommodityTrading Multi-Agent System Blueprint

## Project Overview
**Target Commodity:** ICE Cotton No.2 Futures
**Deliverable:** Comprehensive HTML analysis report with visual supports

---

## Architecture Design

### Level 1 Agents (Strategic)

#### 1. Project Manager Agent (PM)
- **Role:** Overall project design and coordination
- **Responsibilities:**
  - Define project scope and deliverables
  - Allocate tasks to Level 2 agents
  - Synthesize final report
  - Ensure consistency across modules

#### 2. Supervisor Agent (SUP)
- **Role:** Quality assurance and validation
- **Responsibilities:**
  - Review PM decisions step-by-step
  - Challenge assumptions and methodology
  - Validate data sources and logic
  - Ensure completeness of analysis

---

### Level 2 Agents (Tactical)

Each task manager has 2 supervising agents for debate rounds.

#### Task Manager 1: Fundamentals Analysis (TM-FUND)
- **Scope:** Supply/demand balance, seasonal patterns, production data
- **Supervisor A (Logic Challenger):** Questions analytical assumptions
- **Supervisor B (Data/Implementation Validator):** Verifies data accuracy and methodology

#### Task Manager 2: News & Policy Analysis (TM-NEWS)
- **Scope:** Recent news, policy changes, weather impacts
- **Supervisor A (Logic Challenger):** Challenges news interpretation
- **Supervisor B (Data/Implementation Validator):** Verifies source credibility

#### Task Manager 3: Market Views Analysis (TM-VIEWS)
- **Scope:** Market consensus, positioning logic, outlook synthesis
- **Supervisor A (Logic Challenger):** Debates market logic soundness
- **Supervisor B (Data/Implementation Validator):** Cross-references multiple sources

#### Task Manager 4: Technical Analysis (TM-TECH)
- **Scope:** Trend analysis, MA levels, support/resistance
- **Supervisor A (Logic Challenger):** Questions technical interpretations
- **Supervisor B (Data/Implementation Validator):** Validates calculations

#### Task Manager 5: Market Structure Analysis (TM-STRUCT)
- **Scope:** Volume, OI analysis, market attention metrics
- **Supervisor A (Logic Challenger):** Challenges structure interpretations
- **Supervisor B (Data/Implementation Validator):** Verifies data processing

#### Task Manager 6: Positioning Analysis (TM-POS)
- **Scope:** COT reports, CTA positioning, crowding metrics
- **Supervisor A (Logic Challenger):** Debates positioning implications
- **Supervisor B (Data/Implementation Validator):** Validates COT data parsing

#### Task Manager 7: Report Generation (TM-REPORT)
- **Scope:** HTML compilation, visualizations, final formatting
- **Supervisor A (Logic Challenger):** Reviews narrative coherence
- **Supervisor B (Data/Implementation Validator):** Validates chart accuracy

---

## Data Sources

### Primary Sources
| Source | Data Type | URL/Method |
|--------|-----------|------------|
| USDA | Cotton supply/demand, WASDE | https://usda.gov |
| ICE | Futures prices, volume, OI | https://www.ice.com |
| CFTC | COT reports | https://www.cftc.gov/MarketReports/CommitmentsofTraders |
| Barchart | Technical data, charts | https://www.barchart.com |
| Reuters/Bloomberg | News, market commentary | Web search |

### Data Collection Rules
1. Always cite source and retrieval date
2. Cross-validate critical data points
3. Use official sources over aggregators when possible
4. Document any data transformations

---

## Debate Protocol

### Round Structure
1. **Task Manager presents** initial analysis
2. **Logic Challenger** raises questions/concerns
3. **Task Manager responds** with clarifications
4. **Data Validator** checks methodology
5. **Final iteration** incorporates feedback
6. **Minimum 2 rounds** per module, more if significant disagreements

### Escalation Rules
- If supervisors disagree after 3 rounds → escalate to Level 1 SUP
- If critical data missing → flag and proceed with caveats
- If conflicting sources → document both views

---

## Module Specifications

### Module 1: Fundamentals
```
Inputs: USDA data, seasonal patterns, production estimates
Outputs: Supply/demand balance assessment, outlook score
Metrics: Global stocks-to-use ratio, US production forecast
```

### Module 2: News & Policy
```
Inputs: Recent news articles, policy announcements
Outputs: News sentiment summary, key event timeline
Metrics: Impact severity rating (1-5)
```

### Module 3: Market Views
```
Inputs: Analyst reports, market commentary
Outputs: Consensus view summary, contrarian indicators
Metrics: Bullish/bearish sentiment score
```

### Module 4: Technical Analysis
```
Inputs: Price data, moving averages
Outputs: Trend assessment, key levels
Metrics: 60MA position, 60-day close comparison
```

### Module 5: Market Structure
```
Inputs: Volume, OI data
Outputs: Attention metrics, crowding assessment
Metrics: 5-day avg volume change, OI percentile
```

### Module 6: Positioning
```
Inputs: COT reports, CTA estimates
Outputs: Positioning summary, change analysis
Metrics: Net spec position percentile, weekly change
```

### Module 7: Report Generation
```
Inputs: All module outputs
Outputs: Final HTML report
Components: Executive summary, detailed sections, charts
```

---

## HTML Report Structure

```
1. Executive Summary
   - Overall Outlook (Bullish/Neutral/Bearish)
   - Key Drivers Summary
   - Risk Factors

2. Fundamentals Section
   - Supply/Demand Table
   - Balance Chart
   - Key Insights

3. News & Policy Section
   - Event Timeline
   - Impact Assessment

4. Market Views Section
   - Consensus Summary
   - Logic Assessment

5. Technical Analysis Section
   - Trend Charts
   - Key Levels Table
   - MA Analysis

6. Market Structure Section
   - Volume/OI Charts
   - Attention Metrics

7. Positioning Section
   - COT Charts
   - CTA Positioning
   - Crowding Metrics

8. Conclusion
   - Synthesis
   - Trading Implications
   - Confidence Level
```

---

## Execution Rules

### Parallelism Strategy
- Level 2 modules 1-6 execute in parallel
- Module 7 waits for all others to complete
- Within each module: research → analysis → debate (sequential)

### Efficiency Guidelines
1. Cache data fetches to avoid redundant requests
2. Share common data between modules via central store
3. Use async operations where possible
4. Batch similar web requests

---

## Quality Gates

| Gate | Criteria | Owner |
|------|----------|-------|
| Data Complete | All required data fetched | TM |
| Logic Validated | 2+ debate rounds passed | SUP-A |
| Data Verified | Sources cited, accuracy checked | SUP-B |
| Integration Ready | Module output formatted | PM |
| Final Review | HTML renders correctly | SUP |

---

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-20 | Initial architecture design |
