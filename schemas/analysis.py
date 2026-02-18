from pydantic import BaseModel
from typing import List, Optional


class InvestmentFormData(BaseModel):
    age: int
    income: float
    risk_tolerance: str
    goals: Optional[str]


class InvestmentType(BaseModel):
    name: str
    allocation_percentage: float


class AnalysisResult(BaseModel):
    summary: str
    recommendations: List[InvestmentType]
    confidence_score: float
