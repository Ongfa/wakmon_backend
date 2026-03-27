from pydantic import BaseModel, Field
from typing import List, Optional


class FinancialInput(BaseModel):
    # Income statement
    revenue: float = Field(..., gt=0)
    gross_profit: float
    operating_income: float
    net_income: float

    # Cash Flow Statement
    operating_cash_flow: float
    capital_expenditure: float

    # Balance sheet
    total_debt: float
    total_equity: float

    current_assets: float
    current_liabilities: float


class FinancialMetrics(BaseModel):
    gross_margin: float
    net_margin: float
    free_cash_flow: float
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]


class RedFlagResult(BaseModel):
    red_flags: List[str]
    risk_score: float  # 0 to 1
    summary: str
