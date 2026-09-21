from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyDetailsRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=15)
    stock_name: str = Field("", max_length=100)
    sector: str = Field("", max_length=50)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        ticker = value.strip().upper()
        if not ticker:
            raise ValueError("Ticker is required")
        return ticker


class FinancialData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    revenue: float = 0
    costOfRevenue: float = 0
    grossProfit: float = 0
    operatingExpenses: float = 0
    operatingIncome: float = 0
    netIncome: float = 0
    totalAssets: float = 0
    totalLiabilities: float = 0
    totalEquity: float = 0
    currentAssets: float = 0
    currentLiabilities: float = 0
    cash: float = 0
    inventory: float = 0
    accountsReceivable: float = 0
    accountsPayable: float = 0
    longTermDebt: float = 0
    operatingCashFlow: float = 0
    investingCashFlow: float = 0
    financingCashFlow: float = 0
    freeCashFlow: float = 0
    capex: float = 0
    marketCap: float = 0
    enterpriseValue: float = 0
    stockPrice: float = 0
    sharesOutstanding: float = 0
    peRatio: float = 0
    pbRatio: float = 0
    evToEbitda: float = 0
    dividendYield: float = 0
    beta: float = 0
    industryPeAvg: float = 0
    sectorGrowthRate: float = 0
    interestRate: float = 0
    inflationRate: float = 0
    gdpGrowth: float = 0
    analysisType: Literal["ma", "capital", "portfolio", "credit"] = "portfolio"
    investmentAmount: float = 0
    targetCompanyName: str = Field(..., min_length=1, max_length=200)


class AnalyzeInvestmentRequest(BaseModel):
    financialData: FinancialData


class MarketPicksResponse(BaseModel):
    stocks: List[dict]


class DiscoverCompaniesResponse(BaseModel):
    companies: List[dict]


class CompanyDetailsResponse(BaseModel):
    company: dict


class AnalyzeInvestmentResponse(BaseModel):
    analysis: dict
    usage: Optional[dict] = None
