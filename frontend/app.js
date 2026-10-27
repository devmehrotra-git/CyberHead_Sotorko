(() => {
  "use strict";

  const form = document.querySelector("#analysis-form");
  const content = document.querySelector("#content");
  const characterCount = document.querySelector("#character-count");
  const errorMessage = document.querySelector("#form-error");
  const button = document.querySelector("#analyze-button");
  const resultSection = document.querySelector("#result-section");
  const resultIcon = document.querySelector("#result-icon");
  const resultEyebrow = document.querySelector("#result-eyebrow");
  const resultTitle = document.querySelector("#result-title");
  const resultSource = document.querySelector("#result-source");
  const resultSummary = document.querySelector("#result-summary");
  const resultExplanation = document.querySelector("#result-explanation");
  const analysisEvidence = document.querySelector("#analysis-evidence");
  const analysisEvidenceTitle = document.querySelector("#analysis-evidence-title");
  const analysisEvidenceList = document.querySelector("#analysis-evidence-list");
  const safetyGuidance = document.querySelector("#safety-guidance");
  const financialRiskWarning = document.querySelector("#financial-risk-warning");
  const modelResult = document.querySelector("#model-result");
  const resultVerdict = document.querySelector("#result-verdict");
  const resultScore = document.querySelector("#result-score");
  const technicalResponse = document.querySelector("#technical-response");
  const resultWarningTitle = document.querySelector("#result-warning-title");
  const resultWarningText = document.querySelector("#result-warning-text");
  const resultWarning = document.querySelector("#result-warning");
  const languageSelector = document.querySelector("#language");
  const languageSupportWarning = document.querySelector("#language-support-warning");
  const screenshotFile = document.querySelector("#screenshot-file");
  const screenshotPreview = document.querySelector("#screenshot-preview");
  const extractButton = document.querySelector("#extract-button");
  const ocrStatus = document.querySelector("#ocr-status");
  const ocrReview = document.querySelector("#ocr-review");
  const ocrText = document.querySelector("#ocr-text");
  const ocrAnalyzeButton = document.querySelector("#ocr-analyze-button");
  const localeButtons = { bn: document.querySelector("#locale-bn"), en: document.querySelector("#locale-en") };
  let interfaceLocale = "bn";
  let lastResponse = null;
  let lastContext = {};

  const copy = {
    bn: {
      chars: (n) => `${n.toLocaleString("bn-BD")} অক্ষর`, selected: (name) => `${name} বেছে নেওয়া হয়েছে। প্রস্তুত হলে লেখা বের করুন।`,
      ocrExtracting: "সার্ভারে স্থানীয়ভাবে লেখা বের করা হচ্ছে...", ocrNoFile: "প্রথমে PNG, JPEG বা WebP স্ক্রিনশট বেছে নিন।", ocrUnexpected: "OCR service থেকে অপ্রত্যাশিত response এসেছে।", ocrReach: "OCR service-এ পৌঁছানো যাচ্ছে না।", ocrEmpty: "যাচাই করার লেখা খালি। আগে লেখা বের করুন বা লিখুন।", ocrReviewStatus: "OCR-এর ভুল থাকতে পারে। বিশ্লেষণের আগে লেখাটি ঠিক করে নিন।", ocrTextConfidence: (n) => ` OCR text confidence: ${n}% — এটি scam confidence নয়।`, ocrLanguageUpdated: (lang) => ` ${lang} ভাষা বেছে নেওয়া হয়েছে; বিশ্লেষণের আগে বদলাতে পারেন।`, ocrChooseLanguage: " চালিয়ে যেতে বিশ্লেষণের ভাষা নিজে বেছে নিন।",
      empty: "পরীক্ষা করার জন্য একটি বার্তা লিখুন বা পেস্ট করুন।", invalidResponse: "সার্ভার থেকে অপ্রত্যাশিত response এসেছে।", unreachable: "সার্ভারে পৌঁছানো যাচ্ছে না। FastAPI চলছে কি না দেখুন।", http422: "নির্বাচিত বিকল্প ও বার্তার লেখা পরীক্ষা করুন।", http500: "সার্ভার request শেষ করতে পারেনি। আবার চেষ্টা করুন।", requestFailed: (n) => `Request ব্যর্থ হয়েছে (HTTP ${n})।`,
      ocrSource: (lang) => `OCR: লেখা বের করে যাচাই করা হয়েছে${lang ? ` · শনাক্ত ভাষা: ${lang}` : ""}।`, ocrSeparate: "স্ক্রিনশট থেকে লেখা বের হয়েছে; এই ফলাফল OCR confidence নয়, text classifier-এর ফলাফল।", ocrUnsupportedOcr: "OCR সফল হয়েছে, কিন্তু এই ভাষার classification পাওয়া যায় না। কোনও safe-or-scam সিদ্ধান্ত নেওয়া হয়নি।", notSupported: "এই input এখনো supported নয়", limitedSummary: "বর্তমান model এই ভাষা বা input নির্ভরযোগ্যভাবে বিশ্লেষণ করতে পারে না। কোনও safe-or-scam সিদ্ধান্ত নেওয়া হয়নি।", unavailableTitle: "Analysis model পাওয়া যাচ্ছে না", unavailableSummary: "English model load করা যায়নি। কোনও safe-or-scam সিদ্ধান্ত নেওয়া হয়নি।", failedTitle: "Analysis শেষ করা যায়নি", failedSummary: "Model error দিয়েছে। কোনও safe-or-scam সিদ্ধান্ত নেওয়া হয়নি।", prototypeResponse: "সতর্কোর prototype response", prototypeTitle: "এটি এখনও সম্পূর্ণ safety assessment নয়", prototypeSummary: "Server একটি prototype response দিয়েছে। বর্তমান engine বার্তাটিকে নির্ভরযোগ্যভাবে safe বা fraudulent হিসেবে classify করেনি।", generalAdvice: "এটি বার্তাটি নিরাপদ বা প্রতারণামুক্ত—এমন নিশ্চয়তা নয়।", modelEyebrow: "English baseline model", modelSummary: "এটি English baseline model-এর ফলাফল—নিশ্চয়তা নয়। বর্তমান model Bengali বা Banglish-এর জন্য validated নয়।", likelyScam: "এই বার্তায় আরও সতর্ক হওয়া দরকার", noRedFlags: "স্পষ্ট কোনো সতর্ক সংকেত পাওয়া যায়নি", verdictScam: "Model result: সম্ভাব্য scam", verdictSuspicious: "Model result: সন্দেহজনক", verdictClear: "Model result: স্পষ্ট সতর্ক সংকেত নেই", modelScore: (n) => `Model scam score: ${n}%`,
      supportBn: "Bengali OCR কাজ করে। সীমিত experimental rule-based signal দেখা যেতে পারে; এটি trained scam classifier নয় এবং no-match নিরাপদ হওয়ার প্রমাণ নয়।", supportBanglish: "Banglish scam classification এখনো supported নয়। এই ভাষায় কোনও safe-or-scam সিদ্ধান্ত নেওয়া হবে না."
    },
    en: {
      chars: (n) => `${n} characters`, selected: (name) => `${name} selected. Extract text when ready.`, ocrExtracting: "Extracting text locally on the server...", ocrNoFile: "Choose a PNG, JPEG, or WebP screenshot first.", ocrUnexpected: "The OCR service returned an unexpected response.", ocrReach: "Could not reach the OCR service.", ocrEmpty: "Review text is empty. Extract or enter text first.", ocrReviewStatus: "OCR can make mistakes. Correct the text before analysis.", ocrTextConfidence: (n) => ` OCR text confidence: ${n}% — this is not scam confidence.`, ocrLanguageUpdated: (lang) => ` Language selector updated to ${lang}; you can change it before analysis.`, ocrChooseLanguage: " Choose the analysis language manually before continuing.",
      empty: "Enter or paste a message to check.", invalidResponse: "The server returned an unexpected response.", unreachable: "Could not reach the server. Make sure FastAPI is running.", http422: "Please check the selected options and message content.", http500: "The server could not complete the request. Try again.", requestFailed: (n) => `Request failed (HTTP ${n}).`, ocrSource: (lang) => `OCR status: text extracted and reviewed before analysis${lang ? ` · detected language: ${lang}` : ""}.`, ocrSeparate: "The screenshot produced text for review; this result comes from the text classifier, not from OCR confidence.", ocrUnsupportedOcr: "OCR succeeded, but classification is not available for this language. No safe-or-scam decision was made.", notSupported: "This input is not supported yet", limitedSummary: "The current model cannot reliably analyze this language or input type. No safe-or-scam decision was made.", unavailableTitle: "The analysis model is unavailable", unavailableSummary: "The English model could not be loaded. No safe-or-scam decision was made.", failedTitle: "Analysis could not be completed", failedSummary: "The model returned an error. No safe-or-scam decision was made.", prototypeResponse: "Sotorko prototype response", prototypeTitle: "This is not a full safety assessment yet", prototypeSummary: "The server returned a prototype response. The current Sotorko engine did not classify this message as reliably safe or fraudulent.", generalAdvice: "This is not proof that a message is safe or fraudulent.", modelEyebrow: "English baseline model", modelSummary: "This is an English baseline model result—not a guarantee. The current model is not validated for Bengali or Banglish.", likelyScam: "This message may need extra caution", noRedFlags: "No obvious red flags were found", verdictScam: "Model result: likely scam", verdictSuspicious: "Model result: suspicious", verdictClear: "Model result: no obvious red flags", modelScore: (n) => `Model scam score: ${n}%`, supportBn: "Bengali OCR works. A limited experimental rule-based signal may appear; it is not a trained scam classifier, and no-match is not proof of safety.", supportBanglish: "Banglish scam classification is not yet supported. No safe-or-scam decision will be made for this language."
    }
  };

  const interfaceCopy = {
    bn: {
      utilityCitizen: "নাগরিক ডিজিটাল নিরাপত্তা সহায়ক", utilityTag: "নিরাপদ থাকুন · যাচাই করে বিশ্বাস করুন", navGuidance: "নিরাপত্তা নির্দেশনা", navCheck: "বার্তা পরীক্ষা করুন", prototype: "প্রোটোটাইপ", languageControl: "🌐 Language / ভাষা", languageHint: "Don't read Bengali? Switch to English.", serviceKicker: "ডিজিটাল নিরাপত্তা সেবা", heroTitleA: "থামুন। যাচাই করুন।", heroTitleB: "তারপর সিদ্ধান্ত নিন।", heroLede: "কোনও সন্দেহজনক বার্তা বা স্ক্রিনশটের উত্তর দেওয়া, লিঙ্কে ক্লিক করা বা তথ্য শেয়ার করার আগে সতর্কো আপনাকে তা বুঝে নিতে সাহায্য করে।", heroAction: "বার্তা পরীক্ষা করুন", heroLearn: "নিরাপত্তার সহজ নিয়ম জানুন", howLabel: "কীভাবে কাজ করে", heroPanelTitle: "একবারে একটি সাবধানী সিদ্ধান্ত নিন।", stepOne: "বার্তা লিখুন বা স্ক্রিনশট দিন।", stepTwo: "বিশ্লেষণের আগে বের করা লেখা যাচাই করুন।", stepThree: "ফলাফলকে নির্দেশনা হিসেবে দেখুন, নিশ্চয়তা হিসেবে নয়।", messageKicker: "বার্তা পরীক্ষা", workspaceTitle: "বিশ্বাস করার আগে যাচাই করুন।", secretHint: "পাসওয়ার্ড, PIN বা OTP কখনও লিখবেন না।", languageSupportSummary: "ভাষা সহায়তা", englishAvailable: "English classification available", englishAvailableFull: "ইংরেজি লেখার classification চালু আছে।", languageSupportDetail: "বাংলা ও বাংলিশের scam classification এখনো সমর্থিত নয়। বাংলা OCR আলাদাভাবে কাজ করে এবং বের করা লেখা বিশ্লেষণের আগে সম্পাদনা করা যায়।", stepLabel: "ধাপ ১", giveMessage: "বার্তাটি দিন", giveMessageHelp: "সম্পূর্ণ লেখা দিন, যাতে প্রয়োজনীয় প্রসঙ্গ থাকে।", optional: "ঐচ্ছিক", ocrTitle: "অথবা স্ক্রিনশট থেকে লেখা বের করুন", localOcr: "লোকাল OCR", ocrHelp: "বার্তার স্ক্রিনশট দিন, বের করা লেখা যাচাই করুন, তারপর বিশ্লেষণ করুন।", chooseScreenshot: "স্ক্রিনশট বেছে নিন", extractText: "লেখা বের করুন", reviewText: "বের করা লেখা যাচাই করুন", ocrReviewHelp: "OCR ভুল করতে পারে। বিশ্লেষণের আগে লেখাটি ঠিক করে নিন।", analyzeReviewed: "যাচাই করা লেখা বিশ্লেষণ করুন", messageLabel: "যে বার্তাটি পরীক্ষা করবেন", messageHelp: "প্রেরক, লিঙ্ক, কী চাওয়া হচ্ছে এবং কোনও সময়সীমা থাকলে তা রাখুন।", languageLabel: "বার্তার ভাষা", langAuto: "স্বয়ংক্রিয় শনাক্তকরণ (সীমিত)", langBn: "বাংলা", langBanglish: "বাংলিশ", langEn: "ইংরেজি", langHi: "হিন্দি", inputTypeLabel: "বার্তার ধরন", inputText: "লেখা / SMS", inputUrl: "ওয়েব লিঙ্ক", incidentLabel: "আপনার কী হয়েছে?", incidentUnknown: "নিশ্চিত নই", incidentNotLost: "টাকা হারাইনি", incidentLost: "টাকা হারিয়েছি", analyzeMessage: "বার্তা বিশ্লেষণ করুন →", analyzing: "বিশ্লেষণ হচ্ছে...", safetyBasics: "নিরাপত্তার সহজ নিয়ম", safetyTitle: "এই তিনটি অভ্যাস আপনাকে সুরক্ষিত রাখে", safetyIntro: "এগুলি সাধারণ পরামর্শ—আপনার বার্তার ফলাফল নয়।", pause: "থামুন", pauseDetail: "অচেনা লিঙ্কে ক্লিক করার আগে।", verify: "যাচাই করুন", verifyDetail: "নিজে খুঁজে পাওয়া অফিসিয়াল যোগাযোগ মাধ্যমে।", protect: "রক্ষা করুন", protectDetail: "OTP, PIN, password ও পেমেন্টের তথ্য।", stayAlert: "সতর্ক থাকুন", doubtAdvice: "সন্দেহ হলে নিজে যাচাই না করা পর্যন্ত উত্তর দেবেন না।", resultEyebrow: "সতর্কোর ফলাফল", resultTitle: "ফলাফলটি মন দিয়ে পড়ুন।", generalGuidance: "সাধারণ নিরাপত্তা পরামর্শ", notGuarantee: "এটি বার্তাটি নিরাপদ বা প্রতারণামুক্ত—এমন নিশ্চয়তা নয়।", technicalResponse: "প্রযুক্তিগত API response দেখুন", team: "Team CyberHead", footer: "ডিজিটাল নিরাপত্তার প্রোটোটাইপ · সতর্ক থাকুন, যাচাই করুন"
    },
    en: {
      utilityCitizen: "Citizen digital safety companion", utilityTag: "Stay alert · verify before you trust", navGuidance: "Safety guidance", navCheck: "Check a message", prototype: "Prototype", languageControl: "🌐 Language / ভাষা", languageHint: "বাংলায় ফিরতে “বাংলা” নির্বাচন করুন।", serviceKicker: "DIGITAL SAFETY SERVICE", heroTitleA: "Pause. Check.", heroTitleB: "Then decide.", heroLede: "Sotorko helps you examine a suspicious message or screenshot before you click, reply, or share information.", heroAction: "Check a message", heroLearn: "Learn the safety basics", howLabel: "HOW IT WORKS", heroPanelTitle: "Make one careful decision at a time.", stepOne: "Paste a message or upload a screenshot.", stepTwo: "Review the extracted text before sending it.", stepThree: "Read the result as guidance, never a guarantee.", messageKicker: "MESSAGE CHECK", workspaceTitle: "Check before you trust.", secretHint: "Never enter passwords, PINs, or OTPs.", languageSupportSummary: "Language support", englishAvailable: "English classification available", englishAvailableFull: "English text classification is available.", languageSupportDetail: "Bengali and Banglish scam classification are not yet supported. Bengali OCR works independently and extracted text remains editable before analysis.", stepLabel: "STEP 1", giveMessage: "Give us the message", giveMessageHelp: "Paste the complete text so its context is preserved.", optional: "OPTIONAL", ocrTitle: "Or extract text from a screenshot", localOcr: "LOCAL OCR", ocrHelp: "Upload a message screenshot, review the extracted text, then choose when to analyze it.", chooseScreenshot: "Choose screenshot", extractText: "Extract text", reviewText: "Review extracted text", ocrReviewHelp: "OCR can make mistakes. Correct the text before analysis.", analyzeReviewed: "Analyze reviewed text", messageLabel: "Message to check", messageHelp: "Include the sender, link, request, and any deadline if present.", languageLabel: "Message language", langAuto: "Auto-detect (limited)", langBn: "Bengali / বাংলা", langBanglish: "Banglish / বাংলিশ", langEn: "English", langHi: "Hindi / हिन्दी", inputTypeLabel: "Input type", inputText: "Text / SMS", inputUrl: "Web link", incidentLabel: "Incident status", incidentUnknown: "Not sure", incidentNotLost: "No money lost", incidentLost: "Money lost", analyzeMessage: "Analyze message →", analyzing: "Analyzing...", safetyBasics: "SAFETY BASICS", safetyTitle: "Three habits that protect you", safetyIntro: "General guidance only — these are not findings from your message.", pause: "Pause", pauseDetail: "before clicking an unfamiliar link.", verify: "Verify", verifyDetail: "through an official contact channel you find yourself.", protect: "Protect", protectDetail: "OTPs, PINs, passwords, and payment details.", stayAlert: "Stay alert", doubtAdvice: "When in doubt, do not respond until you have checked independently.", resultEyebrow: "SOTORKO RESPONSE", resultTitle: "Review the result carefully.", generalGuidance: "General safety guidance", notGuarantee: "This is not proof that a message is safe or fraudulent.", technicalResponse: "View technical API response", team: "Team CyberHead", footer: "Prototype digital-safety service · Stay alert, verify first"
    }
  };

  interfaceCopy.bn.languageSupportDetail = "বাংলায় সীমিত experimental rule-based signal চালু আছে; এটি trained scam classifier নয়। বাংলিশের classification এখনো সমর্থিত নয়। বাংলা OCR আলাদাভাবে কাজ করে এবং বের করা লেখা বিশ্লেষণের আগে সম্পাদনা করা যায়।";
  interfaceCopy.en.languageSupportDetail = "Bengali has a limited experimental rule-based signal, not a trained scam classifier. Banglish classification is not yet supported. Bengali OCR works independently and extracted text remains editable before analysis.";

  const interfaceExtras = {
    bn: { brandTag: "Sotorko · সতর্ক থাকুন", messageLabelSecondary: "সন্দেহজনক বার্তা", languageSecondary: "ভাষা", numberOne: "০১", numberTwo: "০২", numberThree: "০৩" },
    en: { brandTag: "Sotorko · Be alert", messageLabelSecondary: "Suspicious message", languageSecondary: "Language", numberOne: "01", numberTwo: "02", numberThree: "03" }
  };

  copy.bn.financialRiskWarning = "নিরাপত্তা যাচাই: এই বার্তায় টাকা পাঠানো বা transfer করার অনুরোধ আছে। টাকা দেওয়ার আগে প্রাপক ও কারণটি আলাদা পথে যাচাই করুন। এটি model-এর verdict নয়।";
  copy.en.financialRiskWarning = "Safety check: this message asks you to send or transfer money. Verify the recipient and reason independently before paying. This is separate from the ML verdict.";
  copy.bn.bengaliExperimental = "বাংলা experimental rule-based signal";
  copy.bn.bengaliInconclusive = "পর্যাপ্ত rule-based evidence মেলেনি";
  copy.bn.bengaliInconclusiveSummary = "কোনও পরিচিত সতর্কতার ধরন এই বার্তার সঙ্গে মেলেনি। এটি নিরাপদ হওয়ার প্রমাণ নয়।";
  copy.bn.bengaliSuspicious = "কিছু সতর্ক সংকেত পাওয়া গেছে";
  copy.bn.evidenceTitle = "যে evidence দেখা গেছে";
  copy.bn.englishExperimental = "English experimental safety check";
  copy.bn.ruleWarningTitle = "কিছু সতর্ক সংকেত পাওয়া গেছে";
  copy.en.bengaliExperimental = "Experimental Bengali rule-based signal";
  copy.en.bengaliInconclusive = "No sufficient rule-based evidence was found";
  copy.en.bengaliInconclusiveSummary = "No known warning pattern matched this message. This does not prove it is safe.";
  copy.en.bengaliSuspicious = "Some warning signals were found";
  copy.en.evidenceTitle = "Evidence observed";
  copy.en.englishExperimental = "Experimental English safety check";
  copy.en.ruleWarningTitle = "Warning signals were found";

  const t = (key, ...args) => {
    const value = copy[interfaceLocale][key];
    return typeof value === "function" ? value(...args) : value;
  };

  const updateCharacterCount = () => { characterCount.textContent = t("chars", content.value.length); };

  const setInterfaceLocale = (locale) => {
    interfaceLocale = locale === "en" ? "en" : "bn";
    document.documentElement.lang = interfaceLocale;
    document.documentElement.dir = "ltr";
    document.querySelector(".locale-switch").setAttribute("aria-label", interfaceLocale === "bn" ? "ভাষা / Language" : "Language / ভাষা");
    document.querySelector(".brand").setAttribute("aria-label", interfaceLocale === "bn" ? "সতর্কো হোম" : "Sotorko home");
    document.querySelector(".site-nav").setAttribute("aria-label", interfaceLocale === "bn" ? "প্রধান নেভিগেশন" : "Primary navigation");
    document.querySelector(".hero-panel").setAttribute("aria-label", interfaceLocale === "bn" ? "সতর্কো কীভাবে কাজ করে" : "How Sotorko works");
    document.querySelectorAll(".label-bengali").forEach((element) => { element.lang = interfaceLocale; });
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const value = interfaceCopy[interfaceLocale][element.dataset.i18n] ?? interfaceExtras[interfaceLocale][element.dataset.i18n] ?? copy[interfaceLocale][element.dataset.i18n];
      if (value !== undefined && typeof value !== "function") element.textContent = value;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = interfaceLocale === "bn" ? "বার্তাটি এখানে পেস্ট করুন..." : "Paste the message here..."; });
    localeButtons.bn.classList.toggle("is-selected", interfaceLocale === "bn"); localeButtons.en.classList.toggle("is-selected", interfaceLocale === "en");
    localeButtons.bn.setAttribute("aria-pressed", String(interfaceLocale === "bn")); localeButtons.en.setAttribute("aria-pressed", String(interfaceLocale === "en"));
    updateCharacterCount(); updateLanguageSupportWarning();
    if (lastResponse && !resultSection.hidden) showResult(lastResponse, lastContext, false);
  };

  const showError = (message) => { errorMessage.textContent = message; errorMessage.hidden = false; };
  const clearError = () => { errorMessage.textContent = ""; errorMessage.hidden = true; };
  const setLoading = (isLoading) => { button.disabled = isLoading; button.classList.toggle("is-loading", isLoading); };
  const setOcrStatus = (message, kind = "") => { ocrStatus.textContent = message; ocrStatus.className = `ocr-status ${kind}`.trim(); ocrStatus.hidden = !message; };
  const setOcrLoading = (isLoading) => { extractButton.disabled = isLoading; extractButton.classList.toggle("is-loading", isLoading); extractButton.textContent = isLoading ? (interfaceLocale === "bn" ? "লেখা বের হচ্ছে..." : "Extracting...") : (interfaceLocale === "bn" ? "লেখা বের করুন" : "Extract text"); };

  const updateLanguageSupportWarning = () => {
    if (languageSelector.value === "bn") { languageSupportWarning.textContent = t("supportBn"); languageSupportWarning.hidden = false; }
    else if (languageSelector.value === "banglish") { languageSupportWarning.textContent = t("supportBanglish"); languageSupportWarning.hidden = false; }
    else { languageSupportWarning.textContent = ""; languageSupportWarning.hidden = true; }
  };

  const applyDetectedLanguage = (detectedLanguage) => {
    const supportedOptions = new Set([...languageSelector.options].map((option) => option.value));
    if (detectedLanguage && detectedLanguage !== "auto" && supportedOptions.has(detectedLanguage)) { languageSelector.value = detectedLanguage; updateLanguageSupportWarning(); return true; }
    return false;
  };

  const hasDirectMoneyTransferSignal = (text) => {
    const value = String(text || "").toLowerCase();
    const hasAmount = /(?:₹|\b(?:rs\.?|inr|rupees?)\s*[\d,]+|\b[\d,]+\s*(?:rs\.?|inr|rupees?))/i.test(value);
    const asksToTransfer = /\b(?:send|transfer|wire|deposit)\b.{0,45}\b(?:me|only|now|immediately|urgently|account|number)\b/i.test(value);
    const hasExplicitPaymentEvidence = /\b(?:pay|send|transfer|wire|deposit|remit)\b.{0,45}(?:money|funds?|payment|fee|charge|cash|amount|rupees?|rs\.?|inr|dollars?|₹|\$|[\d,]+)/i.test(value) || /(?:money|funds?|payment|fee|charge|cash|amount|rupees?|rs\.?|inr|dollars?|₹|\$|[\d,]+).{0,45}\b(?:pay|send|transfer|wire|deposit|remit)\b/i.test(value);
    const paymentThreat = hasExplicitPaymentEvidence && (/\b(?:pay|payment|fee|send|transfer|deposit|wire|remit)\b.{0,70}\b(?:immediately|urgent(?:ly)?|blocked|suspended|closed|deactivated)\b/i.test(value) || /\b(?:blocked|suspended|closed|deactivated)\b.{0,70}\b(?:pay|payment|fee|send|transfer|deposit|wire|remit)\b/i.test(value));
    const ordinaryContext = /\b(?:shared lunch|lunch|dinner|split|reimburse(?:ment)?|friend|friends|family|bill|invoice|salary|rent|subscription|purchase|receipt|official app|monthly payment)\b/i.test(value);
    return (!ordinaryContext && hasAmount && asksToTransfer) || (!ordinaryContext && paymentThreat);
  };

  const updateFinancialRiskWarning = (text) => {
    const visible = hasDirectMoneyTransferSignal(text);
    financialRiskWarning.textContent = visible ? t("financialRiskWarning") : "";
    financialRiskWarning.hidden = !visible;
  };

  const localizedExplanation = (response) => {
    if (response.analysis_mode === "bengali_experimental_rules") return interfaceLocale === "en" ? (response.verdict === "suspicious" ? "The experimental Bengali rules found a combination of warning indicators. This is not a trained classifier or a guarantee." : t("bengaliInconclusiveSummary")) : response.explanation || "";
    if (response.analysis_mode === "english_experimental_rules" && interfaceLocale === "bn") return "English experimental safety check-এ সতর্ক সংকেত পাওয়া গেছে। এটি trained classifier-এর নিশ্চিত রায় নয়।";
    if (interfaceLocale === "en") return response.explanation || "";
    if (response.status === "unsupported") return response.explanation?.includes("URL") ? "URL analysis এই model-এ supported নয়। কোনও URL classification করা হয়নি।" : "বর্তমান model শুধু English text-এর জন্য validated। এই ভাষায় নির্ভরযোগ্য classification করা হয়নি।";
    if (response.status === "unavailable") return "English analysis model পাওয়া যাচ্ছে না বা compatible নয়। কোনও নির্ভরযোগ্য classification করা হয়নি।";
    if (response.status === "failed") return "বার্তাটি বিশ্লেষণ করার সময় model error দিয়েছে। কোনও নির্ভরযোগ্য classification করা হয়নি।";
    if (response.verdict === "likely_scam") return "English baseline model-এর prediction: সম্ভাব্য scam। এই score model-এর অনুমান, নিশ্চয়তা নয়। প্রেরক নিজে যাচাই করুন এবং গোপন তথ্য শেয়ার করবেন না।";
    return "English baseline model-এর prediction: স্পষ্ট কোনো সতর্ক সংকেত পাওয়া যায়নি। এটি বার্তাটি নিরাপদ হওয়ার প্রমাণ নয়; প্রেরক নিজে যাচাই করুন।";
  };

  const showResult = (response, context = {}, shouldScroll = true) => {
    lastResponse = response;
    lastContext = context;
    const status = response.status || (response.verdict === "unsupported" ? "unsupported" : "predicted");
    const isBengaliExperimental = response.analysis_mode === "bengali_experimental_rules"; const isEnglishExperimental = response.analysis_mode === "english_experimental_rules"; const isExperimentalRules = isBengaliExperimental || isEnglishExperimental; const isUnsupported = status === "unsupported"; const isUnavailable = status === "unavailable"; const isFailed = status === "failed"; const isGenericLimited = !isExperimentalRules && (isUnsupported || isUnavailable || isFailed);
    const isPlaceholder = response.verdict === "no_obvious_red_flags" && typeof response.explanation === "string" && response.explanation.toLowerCase().includes("not implemented");
    modelResult.hidden = isGenericLimited || isPlaceholder || isExperimentalRules; analysisEvidence.hidden = !isExperimentalRules || !response.evidence?.length; analysisEvidenceTitle.textContent = t("evidenceTitle"); analysisEvidenceList.replaceChildren(...(response.evidence || []).map((item) => { const li = document.createElement("li"); li.textContent = item; return li; })); safetyGuidance.hidden = !response.safety_guidance; safetyGuidance.textContent = response.safety_guidance || ""; resultWarning.hidden = isExperimentalRules; resultSource.hidden = !context.fromOcr; resultSource.textContent = context.fromOcr ? t("ocrSource", context.detectedLanguage) : "";
    resultWarningTitle.textContent = context.fromOcr ? (interfaceLocale === "bn" ? "OCR ও classification আলাদা" : "OCR and classification are separate") : (interfaceLocale === "bn" ? "সাধারণ নিরাপত্তা পরামর্শ" : "General safety guidance"); resultWarningText.textContent = context.fromOcr ? t("ocrSeparate") : t("generalAdvice");
    if (isBengaliExperimental || isEnglishExperimental) { resultIcon.className = "result-icon model-limited"; resultIcon.textContent = "!"; resultEyebrow.textContent = isBengaliExperimental ? t("bengaliExperimental") : t("englishExperimental"); resultTitle.textContent = response.verdict === "suspicious" ? (isBengaliExperimental ? t("bengaliSuspicious") : t("ruleWarningTitle")) : t("bengaliInconclusive"); resultSummary.textContent = response.verdict === "suspicious" ? t("generalAdvice") : ""; }
    else if (isGenericLimited) { resultIcon.className = "result-icon model-limited"; resultIcon.textContent = "!"; resultEyebrow.textContent = isUnavailable ? t("unavailableTitle") : isFailed ? t("failedTitle") : (interfaceLocale === "bn" ? "সীমিত বিশ্লেষণ" : "Limited analysis"); resultTitle.textContent = isUnavailable ? t("unavailableTitle") : isFailed ? t("failedTitle") : t("notSupported"); resultSummary.textContent = isUnavailable ? t("unavailableSummary") : isFailed ? t("failedSummary") : t("limitedSummary"); if (context.fromOcr && isUnsupported) resultWarningText.textContent = t("ocrUnsupportedOcr"); }
    else if (isPlaceholder) { resultIcon.className = "result-icon model-limited"; resultIcon.textContent = "i"; resultEyebrow.textContent = t("prototypeResponse"); resultTitle.textContent = t("prototypeTitle"); resultSummary.textContent = t("prototypeSummary"); resultVerdict.textContent = interfaceLocale === "bn" ? "Prototype response" : "Prototype response"; resultScore.textContent = interfaceLocale === "bn" ? "কোনও model score নেই" : "No model score"; }
    else { resultIcon.className = response.verdict === "likely_scam" ? "result-icon model-positive" : "result-icon model-limited"; resultIcon.textContent = response.verdict === "likely_scam" ? "!" : "i"; resultEyebrow.textContent = t("modelEyebrow"); resultTitle.textContent = response.verdict === "likely_scam" ? t("likelyScam") : t("noRedFlags"); resultSummary.textContent = t("modelSummary"); const verdictLabels = { likely_scam: t("verdictScam"), suspicious: t("verdictSuspicious"), no_obvious_red_flags: t("verdictClear") }; resultVerdict.textContent = verdictLabels[response.verdict] || response.verdict; resultScore.textContent = t("modelScore", (response.risk_score * 100).toFixed(1)); }
    resultExplanation.textContent = localizedExplanation(response); resultExplanation.hidden = !response.explanation; technicalResponse.textContent = JSON.stringify(response, null, 2); resultSection.hidden = false; if (shouldScroll) resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    updateFinancialRiskWarning(context.submittedText);
  };

  const explainHttpError = async (response) => { if (response.status === 422) return t("http422"); if (response.status >= 500) return t("http500"); return t("requestFailed", response.status); };
  const submitAnalysis = async (text, context = {}) => { clearError(); resultSection.hidden = true; setLoading(true); const payload = { input_type: document.querySelector("#input-type").value, content: text, language: languageSelector.value, incident_status: document.querySelector("#incident-status").value };
    try { const response = await fetch("/api/v1/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!response.ok) throw new Error(await explainHttpError(response)); const data = await response.json(); const validScore = data && (data.risk_score === null || typeof data.risk_score === "number"); if (!data || typeof data !== "object" || typeof data.verdict !== "string" || !validScore) throw new Error(t("invalidResponse")); if (payload.language === "auto" && data.detected_language) applyDetectedLanguage(data.detected_language); showResult(data, { ...context, submittedText: text }); } catch (error) { showError(error instanceof TypeError ? t("unreachable") : error.message); } finally { setLoading(false); }
  };

  content.addEventListener("input", updateCharacterCount); languageSelector.addEventListener("change", updateLanguageSupportWarning); localeButtons.bn.addEventListener("click", () => setInterfaceLocale("bn")); localeButtons.en.addEventListener("click", () => setInterfaceLocale("en"));
  form.addEventListener("submit", async (event) => { event.preventDefault(); if (!content.value.trim()) { showError(t("empty")); content.focus(); return; } await submitAnalysis(content.value.trim()); });
  screenshotFile.addEventListener("change", () => { const file = screenshotFile.files?.[0]; ocrReview.hidden = true; ocrText.value = ""; ocrText.dataset.detectedLanguage = ""; setOcrStatus(""); resultSection.hidden = true; if ([...languageSelector.options].some((option) => option.value === "auto")) { languageSelector.value = "auto"; updateLanguageSupportWarning(); } if (!file) { screenshotPreview.hidden = true; screenshotPreview.removeAttribute("src"); return; } screenshotPreview.src = URL.createObjectURL(file); screenshotPreview.hidden = false; setOcrStatus(t("selected", file.name)); });
  extractButton.addEventListener("click", async () => { const file = screenshotFile.files?.[0]; if (!file) { setOcrStatus(t("ocrNoFile"), "error"); return; } setOcrLoading(true); setOcrStatus(t("ocrExtracting")); const formData = new FormData(); formData.append("file", file); formData.append("language", languageSelector.value);
    try { const response = await fetch("/api/v1/analyze/screenshot", { method: "POST", body: formData }); const data = await response.json(); if (!response.ok || !data || typeof data.status !== "string") throw new Error(t("ocrUnexpected")); if (data.status !== "success") { ocrReview.hidden = true; setOcrStatus(data.message || (interfaceLocale === "bn" ? "স্ক্রিনশট পড়া যায়নি।" : "The screenshot could not be read."), data.status === "unavailable" ? "warning" : "error"); return; } ocrText.value = data.extracted_text || ""; ocrText.dataset.detectedLanguage = data.detected_language || "auto"; ocrReview.hidden = false; const languageUpdated = applyDetectedLanguage(data.detected_language); const confidence = typeof data.ocr_confidence === "number" ? t("ocrTextConfidence", (data.ocr_confidence * 100).toFixed(0)) : ""; const languageNote = languageUpdated ? t("ocrLanguageUpdated", data.detected_language) : t("ocrChooseLanguage"); setOcrStatus(`${data.message || (interfaceLocale === "bn" ? "লেখা বের হয়েছে।" : "Text extracted.")}${languageNote}${confidence}`, "success"); } catch (error) { setOcrStatus(error instanceof TypeError ? t("ocrReach") : error.message, "error"); } finally { setOcrLoading(false); }
  });
  ocrAnalyzeButton.addEventListener("click", async () => { const text = ocrText.value.trim(); if (!text) { setOcrStatus(t("ocrEmpty"), "error"); return; } content.value = text; updateCharacterCount(); await submitAnalysis(text, { fromOcr: true, detectedLanguage: ocrText.dataset.detectedLanguage || languageSelector.value }); });
  setInterfaceLocale("bn");
})();
