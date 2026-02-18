# App 05: Financial Report Analyzer

**CAG Technique: Structured Data CAG**

## What This App Teaches
How CAG can augment LLM analysis with **financial formulas, ratio benchmarks, and red flag detection rules** — providing analyst-grade insights without requiring a financial database.

## CAG vs RAG Difference
| | RAG Approach | CAG Approach (this app) |
|---|---|---|
| Knowledge | Financial reports in vector DB | 7 formula/metric cards in memory |
| Retrieval | Find similar report paragraphs | Match financial terms to exact formulas |
| Strength | Good for citing specific reports | **Better for applying formulas** |
| Limitation | May miss cross-report patterns | Knowledge scope limited to curated rules |

## Knowledge Base (7 items)
- `revenue_analysis` — YoY/QoQ growth, CAGR formula
- `profit_margins` — Gross/Operating/Net margin formulas, SaaS benchmarks
- `liquidity` — Current/Quick/Cash ratio calculations
- `debt_analysis` — D/E ratio, interest coverage
- `cash_flow` — OCF vs Net Income, FCF calculation
- `valuation` — P/E, P/S, EV/EBITDA comparisons
- `red_flags` — Revenue recognition, receivables growth, auditor changes

## Test Results ✅

**Query**: _"Analyze the profit margins for a SaaS company with 60% gross margin"_

| Metric | Value |
|---|---|
| Response Length | 3,688 chars (most detailed) |
| Context Chunks | 5 |
| Sources Retrieved | `profit_margins`, `red_flags`, `valuation`, `revenue_analysis`, `liquidity` |
| Avg Relevance | 0.73 |
| Generation Time | 10,833ms |

## Quick Start
```bash
cd backend && py main.py    # Port 8005
cd frontend && npm start    # Port 3005
```
