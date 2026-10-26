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
    """Assessment states returned by the live or limited analysis service."""

    NO_OBVIOUS_RED_FLAGS = "no_obvious_red_flags"
    SUSPICIOUS = "suspicious"
    LIKELY_SCAM = "likely_scam"
    UNSUPPORTED = "unsupported"


class AnalysisStatus(str, Enum):
    """Operational state of the analysis response."""

    PREDICTED = "predicted"
    UNSUPPORTED = "unsupported"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class ScamCategory(str, Enum):
    """Locked Sotorko scam categories."""

    BANKING_PAYMENT = "banking_payment"
    GOVERNMENT_UTILITY = "government_utility"
    EMPLOYMENT_FINANCIAL_OPPORTUNITY = "employment_financial_opportunity"
    IDENTITY_ACCOUNT = "identity_account"
    NONE = "none"


class RedFlag(str, Enum):
    """Supported evidence flags used by the experimental detector."""

    URGENCY = "urgency"
    THREAT = "threat"
    OTP_REQUEST = "otp_request"
    CREDENTIAL_REQUEST = "credential_request"
    PAYMENT_REQUEST = "payment_request"
    SUSPICIOUS_URL = "suspicious_url"
    IMPERSONATION = "impersonation"
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    REWARD_CLAIM = "reward_claim"
    JOB_OFFER = "job_offer"
    ACCOUNT_BLOCK_THREAT = "account_block_threat"


class RecommendedAction(str, Enum):
    """Safe next steps that may be shown with an analysis result."""

    DO_NOT_SHARE_SECRETS = "do_not_share_secrets"
    VERIFY_SENDER = "verify_sender"
    DO_NOT_PAY = "do_not_pay"


class ReportingGuidance(BaseModel):
    """Placeholder reporting guidance returned by the scaffold."""

    available: bool = False
    message: str


class OCRStatus(str, Enum):
    """Status of screenshot text extraction."""

    SUCCESS = "success"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"
    FAILED = "failed"


class OCRResponse(BaseModel):
    """Response returned by the screenshot OCR endpoint."""

    status: OCRStatus
    filename: str
    extracted_text: str = ""
    detected_language: InputLanguage = InputLanguage.AUTO
    ocr_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    message: str
    available_languages: list[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """Request body for content analysis."""

    input_type: InputType
    content: str = Field(..., min_length=1)
    language: InputLanguage
    incident_status: IncidentStatus


class AnalysisResponse(BaseModel):
    """Contract response returned by the analysis endpoint."""

    status: AnalysisStatus
    verdict: Verdict
    risk_score: float | None = Field(default=None, ge=0.0, le=1.0)
    detected_language: InputLanguage
    output_language: InputLanguage
    scam_category: ScamCategory | None
    red_flags: list[RedFlag]
    explanation: str
    recommended_actions: list[RecommendedAction]
    reporting: ReportingGuidance
    analysis_mode: str = "unsupported"
    evidence: list[str] = Field(default_factory=list)
    safety_guidance: str = ""
