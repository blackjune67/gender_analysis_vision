from pydantic import BaseModel, Field
from typing import List

class GenderResult(BaseModel):
    gender: str = Field(..., description="감지된 성별 (남성 또는 여성)") # "남성" 또는 "여성" 결과값을 한글로 표시했는데, 영어로 표시해도 무방합니다.
    age: int = Field(..., description="추정 나이") # 나이
    confidence: float = Field(..., description="감지 신뢰도 (0.0 ~ 1.0)", ge=0.0, le=1.0) # 신뢰도 (0.0 ~ 1.0)

class GenderDetectionResponse(BaseModel):
    results: List[GenderResult]