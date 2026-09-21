from __future__ import annotations

from app.providers.base import LLMProvider
from app.schemas.research import CompanyDetailsRequest, FinancialData
from app.services.llm import complete_json

JSON_SYSTEM = "You are a financial data assistant. Return ONLY valid JSON, no markdown or code fences."

MARKET_PICKS_PROMPT = """Give me 6 popular stocks from countries that support social inclusivity (single parent policies, pet-friendly workplace policies, cultural diversity). Mix stocks from different countries. Return a JSON object with a "stocks" array where each object has:
- "stock_name": full company name (string)
- "ticker": stock ticker symbol (string)
- "sector": sector name (string)
- "current_price": realistic current price in USD (number)
- "change_percentage": today's percentage change, can be negative (number)
- "description": one-line description including the country of origin and social initiatives (string)

Include a diverse mix of large-cap stocks from different socially inclusive countries. Use realistic approximate USD prices.
"""

DISCOVER_PROMPT = """Give me 8 well-known publicly traded companies from countries that support social inclusivity. These companies should have strong commitments to single parent support, pet-friendly policies, and cultural diversity. Mix companies from different sectors and countries. Return a JSON object with a "companies" array where each object has:
- "stock_name": full company name (string)
- "ticker": stock ticker symbol (string)
- "sector": sector name, use one of: Technology, Consumer Discretionary, Financial Services, Entertainment, Healthcare, Energy (string)
- "current_price": realistic current price in USD (number)
- "change_percentage": today's percentage change, can be negative (number)
- "description": one-line description of the company's social inclusivity commitment (string)
- "single_parent_score": single parent support score 60-100 (number)
- "pet_parent_score": pet-friendly policy score 50-100 (number)
- "intercaste_score": inter-caste diversity score 60-100 (number)
- "intercultural_score": inter-cultural diversity score 70-100 (number)

Use realistic approximate USD prices. Include a diverse mix of sectors.
"""

ANALYZE_SYSTEM = """You are an elite investment analyst. Analyze comprehensive financial data and return ONLY valid JSON in this exact shape:
{
  "recommendation": "INVEST" | "HOLD" | "PASS",
  "confidence": 0-100,
  "riskScore": 0-100,
  "verdict": "2-3 sentence executive summary",
  "keyMetrics": [
    {"name": "metric name", "value": "formatted value", "status": "positive" | "neutral" | "negative", "benchmark": "industry comparison"}
  ],
  "strengths": ["strength 1"],
  "weaknesses": ["weakness 1"],
  "risks": ["risk 1"],
  "opportunities": ["opportunity 1"],
  "detailedAnalysis": {
    "profitability": "analysis text",
    "liquidity": "analysis text",
    "solvency": "analysis text",
    "valuation": "analysis text",
    "cashFlow": "analysis text",
    "marketPosition": "analysis text"
  },
  "projections": {
    "bestCase": {"returnPct": number, "timeline": "timeframe"},
    "baseCase": {"returnPct": number, "timeline": "timeframe"},
    "worstCase": {"returnPct": number, "timeline": "timeframe"}
  },
  "actionItems": ["recommendation 1"]
}
Be quantitative and cite specific numbers from the provided data. You are not a SEBI-registered advisor.
"""

ANALYSIS_TYPE_NAMES = {
    "ma": "Mergers & Acquisitions",
    "capital": "Capital Allocation",
    "portfolio": "Portfolio Risk Assessment",
    "credit": "Credit & Lending Analysis",
}


def _n(value: float) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def company_details_prompt(payload: CompanyDetailsRequest) -> str:
    name = payload.stock_name.strip() or payload.ticker
    sector = payload.sector.strip() or "unknown"
    return f"""Provide comprehensive details for {name} ({payload.ticker}), sector: {sector}.

Return a JSON object with:
- stock_name, ticker, sector, country, description
- single_parent_score, pet_parent_score, intercaste_score, intercultural_score (0-100)
- single_parent_investment, pet_parent_investment (strings like "$50M/year")
- ceo, founded_year, employees, headquarters
- market_cap (string like "$2.5T"), pe_ratio, revenue (string like "$394B"), dividend_yield, beta
- week_52_high, week_52_low, current_price, change_percentage
- price_history: 12 objects with month and price
- ai_recommendation ("Buy", "Hold", or "Sell"), ai_analysis, ai_confidence (0-100)

Use realistic approximate data.
"""


def analyze_prompt(data: FinancialData) -> str:
    kind = ANALYSIS_TYPE_NAMES.get(data.analysisType, data.analysisType)
    return f"""Analyze this investment opportunity for {data.targetCompanyName}.
Analysis type: {kind}
Investment amount: {_n(data.investmentAmount)}

=== INCOME STATEMENT ===
Revenue: {_n(data.revenue)}
Cost of Revenue: {_n(data.costOfRevenue)}
Gross Profit: {_n(data.grossProfit)}
Operating Expenses: {_n(data.operatingExpenses)}
Operating Income: {_n(data.operatingIncome)}
Net Income: {_n(data.netIncome)}

=== BALANCE SHEET ===
Total Assets: {_n(data.totalAssets)}
Total Liabilities: {_n(data.totalLiabilities)}
Total Equity: {_n(data.totalEquity)}
Current Assets: {_n(data.currentAssets)}
Current Liabilities: {_n(data.currentLiabilities)}
Cash: {_n(data.cash)}
Inventory: {_n(data.inventory)}
Accounts Receivable: {_n(data.accountsReceivable)}
Accounts Payable: {_n(data.accountsPayable)}
Long-Term Debt: {_n(data.longTermDebt)}

=== CASH FLOW ===
Operating Cash Flow: {_n(data.operatingCashFlow)}
Investing Cash Flow: {_n(data.investingCashFlow)}
Financing Cash Flow: {_n(data.financingCashFlow)}
Free Cash Flow: {_n(data.freeCashFlow)}
CapEx: {_n(data.capex)}

=== MARKET DATA ===
Market Cap: {_n(data.marketCap)}
Enterprise Value: {_n(data.enterpriseValue)}
Stock Price: {_n(data.stockPrice)}
Shares Outstanding: {_n(data.sharesOutstanding)}
P/E: {_n(data.peRatio)}
P/B: {_n(data.pbRatio)}
EV/EBITDA: {_n(data.evToEbitda)}
Dividend Yield: {_n(data.dividendYield)}%
Beta: {_n(data.beta)}

=== MACRO ===
Industry P/E Average: {_n(data.industryPeAvg)}
Sector Growth Rate: {_n(data.sectorGrowthRate)}%
Interest Rate: {_n(data.interestRate)}%
Inflation Rate: {_n(data.inflationRate)}%
GDP Growth: {_n(data.gdpGrowth)}%
"""


async def fetch_market_picks(provider: LLMProvider) -> dict:
    payload = await complete_json(provider, prompt=MARKET_PICKS_PROMPT, system_prompt=JSON_SYSTEM)
    stocks = payload.get("stocks") if isinstance(payload, dict) else payload
    if not isinstance(stocks, list):
        raise ValueError("Market picks response was not a list")
    return {"stocks": stocks}


async def fetch_discover_companies(provider: LLMProvider) -> dict:
    payload = await complete_json(provider, prompt=DISCOVER_PROMPT, system_prompt=JSON_SYSTEM)
    companies = payload.get("companies") if isinstance(payload, dict) else payload
    if not isinstance(companies, list):
        raise ValueError("Discover response was not a list")
    return {"companies": companies}


async def fetch_company_details(provider: LLMProvider, request: CompanyDetailsRequest) -> dict:
    company = await complete_json(
        provider,
        prompt=company_details_prompt(request),
        system_prompt="You are a financial analyst. Return ONLY valid JSON, no markdown.",
        max_tokens=4096,
    )
    if not isinstance(company, dict):
        raise ValueError("Company details response was not an object")
    company.setdefault("ticker", request.ticker)
    return {"company": company}


async def analyze_investment(provider: LLMProvider, data: FinancialData) -> dict:
    analysis = await complete_json(
        provider,
        prompt=analyze_prompt(data),
        system_prompt=ANALYZE_SYSTEM,
        temperature=0.3,
        max_tokens=4096,
    )
    if not isinstance(analysis, dict):
        raise ValueError("Analysis response was not an object")
    return {"analysis": analysis}
