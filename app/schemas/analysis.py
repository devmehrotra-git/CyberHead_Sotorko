"""Pydantic models for the Sotorko analysis API contract."""

from enum import Enum

from pydantic import BaseModel, Field


class InputType(str, Enum):
    """Type of content submitted for analysis."""

    TEXT = "text"
    URL = "url"


class InputLanguage(str, Enum):
    """Language requested for analysis and output."""

    AUTO = "auto"
    BN = "bn"
    HI = "hi"
    EN = "en"
    BANGLISH = "banglish"


class IncidentStatus(str, Enum):
    """Whether the user has reported a financial loss."""

    UNKNOWN = "unknown"
    NOT_LOST = "not_lost"
    LOST_MONEY = "lost_money"


class Verdict(str, Enum):
    """Scam assessment result values reserved for the analysis engine."""

    NO_OBVIOUS_RED_FLAGS = "no_obvious_red_flags"
    SUSPICIOUS = "suspicious"
    LIKELY_SCAM = "likely_scam"


class ScamCategory(str, Enum):
    """Scam category placeholder values until detection is implemented."""

    NOT_IMPLEMENTED = "not_implemented"


class RedFlag(str, Enum):
    """Red-flag placeholder values until rules are implemented."""

    NOT_IMPLEMENTED = "not_implemented"


class RecommendedAction(str, Enum):
    """Recommended-action placeholder values until analysis is implemented."""

    NOT_IMPLEMENTED = "not_implemented"


class ReportingGuidance(BaseModel):
    """Placeholder reporting guidance returned by the scaffold."""

    available: bool = False
    message: str


class AnalysisRequest(BaseModel):
    """Request body for content analysis."""

    input_type: InputType
    content: str = Field(..., min_length=1)
    language: InputLanguage
    incident_status: IncidentStatus


class AnalysisResponse(BaseModel):
    """Contract response returned by the analysis endpoint."""

    verdict: Verdict
    risk_score: float = Field(..., ge=0.0, le=1.0)
    detected_language: InputLanguage
    output_language: InputLanguage
    scam_category: ScamCategory
    red_flags: list[RedFlag]
    explanation: str
    recommended_actions: list[RecommendedAction]
    reporting: ReportingGuidance
