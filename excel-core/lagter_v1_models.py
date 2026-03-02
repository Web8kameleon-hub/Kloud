from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class LagterKPI(BaseModel):
    name: str
    target: float = Field(ge=0, le=1)
    actual: float = Field(ge=0, le=1)


class LagterLawCheck(BaseModel):
    law: str
    description: str
    pass_rate: float = Field(ge=0, le=1)


class LagterEnigma(BaseModel):
    enigma_id: str
    title: str
    status: Literal["open", "testing", "decoded", "archived"]
    confidence: float = Field(ge=0, le=1)
    hypothesis: str


class LagterSketchPoint(BaseModel):
    day: str
    bio: float = Field(ge=0, le=1)
    behavior: float = Field(ge=0, le=1)
    ambient: float = Field(ge=0, le=1)
    tension: float = Field(ge=0, le=1)


class LagterPayload(BaseModel):
    generated_at: str
    version: str
    kpis: List[LagterKPI]
    law_checks: List[LagterLawCheck]
    enigma_registry: List[LagterEnigma]
    sketch_points: List[LagterSketchPoint]


class LagterMeta(BaseModel):
    module: str
    version: str
    generated_at: str
    sheets: List[str]
    counts: dict


class LagterProcessStep(BaseModel):
    step: str
    input: str
    output: str
    controls: List[str]
