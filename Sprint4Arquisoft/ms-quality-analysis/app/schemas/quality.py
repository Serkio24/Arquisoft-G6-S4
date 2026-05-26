from pydantic import BaseModel
from typing import Optional


class MaintainabilityRating(BaseModel):
    rating: str                         # A, B, C, D, E
    rating_raw: str                     # 1-5
    is_a: bool
    technical_debt_minutes: Optional[str] = None
    debt_ratio_percent: Optional[str] = None
    code_smells: Optional[str] = None


class ASRCompliance(BaseModel):
    compliant: bool
    percent_a: float
    threshold: float
    total_analyses: int
    analyses_with_rating_a: int
    status: str                         # "CUMPLE ASR" o "NO CUMPLE ASR"
