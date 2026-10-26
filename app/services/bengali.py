"""Experimental Bengali scam-signal rules.

This narrow detector produces evidence, not calibrated probabilities or
trained-classifier claims. A no-match result is never treated as genuine.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    InputLanguage,
    RecommendedAction,
    RedFlag,
    ReportingGuidance,
    ScamCategory,
    Verdict,
)


@dataclass(frozen=True)
class BengaliFinding:
    category: ScamCategory
    flags: tuple[RedFlag, ...]
    evidence: tuple[str, ...]


def normalize_for_matching(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", value).strip()


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _protective_advice(text: str) -> bool:
    return _has_any(text, ("কাউকে দেবেন না", "কাউকে দিবেন না", "শেয়ার করবেন না", "শেয়ার করবেন না", "ভাগ করবেন না", "দেওয়া যাবে না", "দেওয়া যাবে না", "প্রকাশ করবেন না", "never share", "do not share"))


def detect(text: str) -> BengaliFinding | None:
    """Return a finding only when a rule has a mechanism plus context."""
    value = normalize_for_matching(text)
    if not value or _protective_advice(value):
        return None

    sensitive = _has_any(value, ("otp", "ওটিপি", "pin", "পিন", "password", "পাসওয়ার্ড", "পাসওয়ার্ড", "kyc", "লগইন", "login"))
    request = _has_any(value, ("দিন", "দাও", "দেন", "পাঠান", "শেয়ার", "শেয়ার", "বলুন", "দেবেন", "প্রবেশ", "enter", "send", "share", "provide", "verify"))
    urgent = _has_any(value, ("জরুরি", "অবিলম্বে", "এখনই", "দ্রুত", "নইলে", "সাথে সাথে", "immediately", "urgent"))
    account = _has_any(value, ("অ্যাকাউন্ট", "একাউন্ট", "ব্যাংক", "bank", "সিম", "sim", "কেওয়াইসি", "kyc"))
    link = bool(re.search(r"https?://|www\.|লিংক|লিঙ্ক|link", value))
    prize = _has_any(value, ("পুরস্কার", "লটারি", "জিতেছেন", "জিতেছ", "বিজয়ী", "বিজয়ী", "প্রাইজ", "রিওয়ার্ড", "রিওয়ার্ড", "reward", "lottery", "winner", "prize"))
    payment = _has_any(value, ("ফি", "টাকা", "পেমেন্ট", "চার্জ", "অগ্রিম", "রেজিস্ট্রেশন", "registration", "fee", "payment", "send money", "pay"))
    job = _has_any(value, ("চাকরি", "নিয়োগ", "নিয়োগ", "জব", "job", "কাজের সুযোগ", "work from home", "আয়", "আয়", "income", "recruit"))

    if sensitive and request:
        flags = [RedFlag.CREDENTIAL_REQUEST]
        evidence = ["সংবেদনশীল তথ্য বা কোড দেওয়ার অনুরোধ পাওয়া গেছে।"]
        if _has_any(value, ("otp", "ওটিপি")):
            flags.append(RedFlag.OTP_REQUEST)
            evidence.append("OTP দেওয়ার অনুরোধ রয়েছে।")
        if urgent:
            flags.append(RedFlag.URGENCY)
        if account and _has_any(value, ("বন্ধ", "ব্লক", "block")):
            flags.append(RedFlag.ACCOUNT_BLOCK_THREAT)
            evidence.append("অ্যাকাউন্ট বন্ধ হওয়ার হুমকি রয়েছে।")
        if link:
            flags.append(RedFlag.SUSPICIOUS_URL)
        return BengaliFinding(
            ScamCategory.IDENTITY_ACCOUNT if link or _has_any(value, ("login", "লগইন")) else ScamCategory.BANKING_PAYMENT,
            tuple(dict.fromkeys(flags)),
            tuple(evidence),
        )

    if urgent and account and (link or sensitive or request):
        flags = [RedFlag.URGENCY, RedFlag.THREAT]
        if link:
            flags.append(RedFlag.SUSPICIOUS_URL)
        if _has_any(value, ("বন্ধ", "ব্লক", "block")):
            flags.append(RedFlag.ACCOUNT_BLOCK_THREAT)
        return BengaliFinding(ScamCategory.IDENTITY_ACCOUNT, tuple(dict.fromkeys(flags)), ("জরুরি হুমকির সঙ্গে অ্যাকাউন্ট বা সিম-সংক্রান্ত পদক্ষেপ চাওয়া হয়েছে।",))

    if prize and payment:
        return BengaliFinding(ScamCategory.BANKING_PAYMENT, (RedFlag.REWARD_CLAIM, RedFlag.PAYMENT_REQUEST), ("পুরস্কার বা লটারির দাবির সঙ্গে ফি/পেমেন্ট চাওয়া হয়েছে।",))

    if job and payment:
        return BengaliFinding(ScamCategory.EMPLOYMENT_FINANCIAL_OPPORTUNITY, (RedFlag.JOB_OFFER, RedFlag.PAYMENT_REQUEST), ("চাকরি বা আয়ের দাবির সঙ্গে অগ্রিম ফি/রেজিস্ট্রেশন পেমেন্ট চাওয়া হয়েছে।",))

    return None


def analyze(request: AnalysisRequest) -> AnalysisResponse:
    finding = detect(request.content)
    common = dict(
        status=AnalysisStatus.PREDICTED if finding else AnalysisStatus.UNSUPPORTED,
        detected_language=InputLanguage.BN,
        output_language=InputLanguage.BN,
        analysis_mode="bengali_experimental_rules",
        reporting=ReportingGuidance(available=False, message="Human reporting guidance is not implemented yet."),
    )
    if finding:
        return AnalysisResponse(
            **common,
            verdict=Verdict.SUSPICIOUS,
            risk_score=None,
            scam_category=finding.category,
            red_flags=list(finding.flags),
            explanation="Experimental Bengali rule-based signal: " + " ".join(finding.evidence) + " এটি প্রশিক্ষিত মডেলের নিশ্চিত রায় নয়।",
            recommended_actions=[RecommendedAction.DO_NOT_SHARE_SECRETS, RecommendedAction.VERIFY_SENDER, RecommendedAction.DO_NOT_PAY],
            evidence=list(finding.evidence),
            safety_guidance="প্রেরক নিজে যাচাই করুন; OTP, PIN, পাসওয়ার্ড বা টাকা পাঠাবেন না। নিয়মভিত্তিক পরীক্ষাটি ভুলও করতে পারে।",
        )
    return AnalysisResponse(
        **common,
        verdict=Verdict.UNSUPPORTED,
        risk_score=None,
        scam_category=None,
        red_flags=[],
        explanation="বাংলা পরীক্ষামূলক নিয়মে পর্যাপ্ত প্রমাণ মেলেনি। এটিকে নিরাপদ বার্তা হিসেবে ধরা যাবে না; প্রেরক নিজে যাচাই করুন।",
        recommended_actions=[RecommendedAction.VERIFY_SENDER],
        evidence=[],
        safety_guidance="কোনও নিয়ম না মেলা নিরাপদ হওয়ার প্রমাণ নয়। সন্দেহ থাকলে উত্তর দেবেন না এবং নিজে যাচাই করুন।",
    )
