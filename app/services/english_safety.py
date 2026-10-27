"""Separate experimental safety checks for English model results."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.schemas.analysis import RedFlag, ScamCategory


@dataclass(frozen=True)
class EnglishSafetyFinding:
    category: ScamCategory
    flags: tuple[RedFlag, ...]
    evidence: tuple[str, ...]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def is_protective_advice(text: str) -> bool:
    """Recognize explicit advice not to disclose authentication credentials."""
    value = _normalize(text)
    return bool(
        re.search(
            r"\b(?:never|don't|do not|dont|shouldn't|should not)\b.{0,24}"
            r"\b(?:share|send|give|provide|disclose|tell)\b.{0,24}"
            r"\b(?:otp|pin|password|passcode|verification code|authentication code|security code)\b",
            value,
        )
    )


def detect(text: str) -> EnglishSafetyFinding | None:
    value = _normalize(text)
    protective = is_protective_advice(text)
    credential_request = bool(re.search(r"\b(?:send|share|provide|give|disclose|tell|enter)\b.{0,32}\b(?:otp|pin|password|passcode|verification code|authentication code|security code)\b", value) or re.search(r"\b(?:otp|pin|password|passcode|verification code|authentication code|security code)\b.{0,32}\b(?:send|share|provide|give|disclose|tell|enter)\b", value))
    if protective or not credential_request:
        credential_request = False

    urgent_threat = bool(re.search(r"\b(?:urgent|immediately|now|soon|within\s+\w+|or\s+else|deduct(?:s|ed)?|debit(?:s|ed)?|blocked|suspended|closed|deactivated)\b", value)) and bool(re.search(r"\b(?:account|bank|banking|sim|money|payment|funds|card)\b", value))
    # A credential request may legitimately use "send" (for example, "send
    # your OTP"). Treat it as a payment demand only when a payment verb is
    # tied to explicit monetary/payment language.
    payment_demand = bool(
        re.search(
            r"\b(?:pay|send|transfer|wire|deposit|remit)\b.{0,45}"
            r"(?:money|funds?|payment|fee|charge|cash|amount|rupees?|rs\.?|inr|dollars?|₹|\$|\d[\d,]*)",
            value,
        )
        or re.search(
            r"(?:money|funds?|payment|fee|charge|cash|amount|rupees?|rs\.?|inr|dollars?|₹|\$|\d[\d,]*)"
            r".{0,45}\b(?:pay|send|transfer|wire|deposit|remit)\b",
            value,
        )
    )
    reward_claim = bool(re.search(r"\b(?:prize|winner|reward|lottery|cashback|claim)\b", value))
    impersonation = bool(re.search(r"\b(?:bank|police|government|official|support|security team)\b", value))

    if not credential_request and not (payment_demand and (urgent_threat or reward_claim or impersonation)):
        return None

    flags: list[RedFlag] = []
    evidence: list[str] = []
    if credential_request:
        flags.extend((RedFlag.CREDENTIAL_REQUEST, RedFlag.OTP_REQUEST) if re.search(r"\b(?:otp|passcode|verification code|authentication code|security code)\b", value) else (RedFlag.CREDENTIAL_REQUEST,))
        evidence.append("Requests the recipient to send or disclose an authentication code or credential.")
    if urgent_threat:
        flags.extend((RedFlag.URGENCY, RedFlag.THREAT))
        evidence.append("Uses urgency or a financial/account threat to prompt action.")
    if payment_demand and (urgent_threat or reward_claim or impersonation):
        flags.append(RedFlag.PAYMENT_REQUEST)
        evidence.append("Combines a payment request with a threat, reward claim, or authority cue.")
    if reward_claim:
        flags.append(RedFlag.REWARD_CLAIM)
    if impersonation:
        flags.append(RedFlag.IMPERSONATION)
    return EnglishSafetyFinding(ScamCategory.BANKING_PAYMENT, tuple(dict.fromkeys(flags)), tuple(evidence))
