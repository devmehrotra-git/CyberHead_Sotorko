# Sotorko Normalized Corpus Audit

Read-only audit of `data/derived/normalized_messages.jsonl` and
`data/derived/review_messages.jsonl`. No source, external, or normalized dataset file was
modified.

## Executive findings

- The corpus contains 20,254 unique texts and 5,127 exact duplicate groups affecting 10,699 records.
- 5,004 duplicate groups cross source boundaries and affect 10,386 records.
- All 638 mapped scam records come from `mendeley_sms_phishing`; all are English and Latin script.
- The mapped scam class is therefore not currently safe for an unbiased train/validation/test split.
- Exact-text grouping must happen before splitting, and groups must be assigned wholly to one split.

## 1. Exact duplicate groups

| Measure | Result |
|---|---:|
| Unique texts | 20,254 |
| Duplicate groups | 5,127 |
| Records affected | 10,699 |
| Largest group | 30 records |

Duplicate-group classification:

| Classification | Groups |
|---|---:|
| `all_mapped_same_label` | 4,251 |
| `mapped_plus_review` | 482 |
| `all_review` | 394 |

Additional duplicate findings:

- Groups containing both mapped `scam` and mapped `genuine`: **0**.
- Groups spanning multiple `source_id` values: **5,004**.
- Groups spanning multiple languages: **0**.
- Groups with different original labels: **496**.
- Every duplicate group having the same effective label: **No**. The difference is caused by
  groups containing mapped records and review records with `null` labels; no group contains both
  mapped scam and mapped genuine labels.

The high cross-source count is partly caused by repeated corpus content and partly by duplicated
rows inside sources. It must be treated as leakage even when the labels happen to agree.

## 2. Cross-source duplication

There are **5,004 cross-source duplicate-text groups** affecting **10,386 records**.

Examples of large groups:

| Group size | Text excerpt | Sources/labels |
|---:|---|---|
| 13 | “I cant pick the phone right now. Pls send a message” | UCI `ham` and Mendeley `ham` |
| 6 | Bengali food-safety public-service message | Bangla `ham`/`spam ` and BTTC `HAM` |
| 5 | “Wen ur lovable bcums angry wid u...” | UCI `ham` and Mendeley `ham` |
| 5 | “Your opinion about me? 1. Over 2. Jada...” | UCI `ham` and Mendeley `ham` |
| 5 | “7 wonders in My WORLD...” | UCI `ham` and Mendeley `ham` |
| 5 | “Please call ... as you have WON...” | Mendeley `Smishing` and UCI `spam` |

The last example is especially important: source-specific mapping can produce a scam/review
boundary around identical text. It must remain one indivisible split group.

## 3. Mapped scam corpus audit

There are **638 mapped scam records**.

### Distributions

| Dimension | Distribution |
|---|---|
| Source | `mendeley_sms_phishing`: 638 |
| Original label | `Smishing`: 616; `smishing`: 22 |
| Language | `en`: 638 |
| Script | `latin`: 638 |

### Message statistics and indicators

- Length: mean **139.59** characters; median **146**; minimum **34**; maximum **383**.
- URL/domain presence: **120** records.
- Phone-number presence: **505** records.
- OTP terminology: **0** records.
- KYC terminology: **23** records.
- Payment/financial terminology (`pay`, `payment`, `fee`, `cash`, `money`, `account`, `bank`,
  `card`, `refund`, `transfer`, `charge`): **146** records.

Keyword counts are document-level presence counts, not occurrence counts:

| Keyword pattern | Scam records |
|---|---:|
| `free` | 90 |
| `win`/`winner`/`prize`/`reward` | 162 |
| `verify`/`verification` | 8 |
| `click`/`link`/`http` | 64 |
| `urgent` | 89 |
| `account` | 38 |

### Twenty representative scam records

All are from the only currently mapped scam source; the sample is distributed across the two
original-label spellings and corpus positions.

1. `mendeley_sms_phishing / row-000256 / Smishing`: “Todays Voda numbers ending 5226 are selected to receive a £350 award. If you have a match please call ...”
2. `mendeley_sms_phishing / row-000810 / Smishing`: “WELL DONE! Your 4* Costa Del Sol Holiday or £5000 await collection. Call ...”
3. `mendeley_sms_phishing / row-001424 / Smishing`: “URGENT! This is the 2nd attempt to contact U! U have WON £1250 ...”
4. `mendeley_sms_phishing / row-001929 / Smishing`: “U have a Secret Admirer who is looking 2 make contact with U...”
5. `mendeley_sms_phishing / row-002631 / Smishing`: “Urgent! Please call ... Your ABTA complimentary 4* Tenerife Holiday or £5000 cash await collection...”
6. `mendeley_sms_phishing / row-003196 / Smishing`: “Please call our customer service representative ... you have WON a guaranteed £2000 cash or £6000 prize!”
7. `mendeley_sms_phishing / row-003787 / Smishing`: “You've won tkts to the EURO2004 CUP FINAL or £800 CASH...”
8. `mendeley_sms_phishing / row-004353 / Smishing`: “Mila, age23, blonde, new in UK. I look sex with UK guys...”
9. `mendeley_sms_phishing / row-004977 / Smishing`: “Dear (paytm)customer your paytm KYC has been suspended... Your Paytm A/C will block within 24hr...”
10. `mendeley_sms_phishing / row-005600 / Smishing`: “We tried to contact you re our offer of New Video Phone ...”
11. `mendeley_sms_phishing / row-001605 / smishing`: “U have a secret admirer. REVEAL who thinks U R So special...”
12. `mendeley_sms_phishing / row-002351 / smishing`: “IMPORTANT INFORMATION 4 ORANGE USER... find out why log onto http://www.urawinner.com”
13. `mendeley_sms_phishing / row-002737 / smishing`: “XMAS REWARD IS WAITING FOR YOU!... receive a £400 reward.”
14. `mendeley_sms_phishing / row-003168 / smishing`: “Camera - You are awarded a SiPix Digital Camera! ... Delivery within 8 days”
15. `mendeley_sms_phishing / row-003776 / smishing`: “important information 4 orange user... log onto http://www.urawinner.com...”
16. `mendeley_sms_phishing / row-004715 / smishing`: “Loan INR5,00,000 - 7,50,000. Homeowners + Tenants welcome...”
17. `mendeley_sms_phishing / row-004801 / smishing`: “important information 4 orange user... today is your lucky day!...”
18. `mendeley_sms_phishing / row-005115 / smishing`: “UR awarded a City Break and could WIN a £200 Summer Shopping spree...”
19. `mendeley_sms_phishing / row-005206 / smishing`: “Dozens of Free Games - with great prizes...”
20. `mendeley_sms_phishing / row-005421 / smishing`: “Congratulations ur awarded 500 of CD vouchers... txt MUSIC to 87066”

These examples show strong prize, premium-rate-call, subscription, KYC, loan, and reward bias.

## 4. Review corpus audit

There are **5,978 review records**. These remain unlabeled and are not treated as scam examples.

| Dimension | Distribution |
|---|---|
| Source | UCI: 747; Mendeley SMS: 489; Bangla SMS: 2,058; BTTC: 2,684 |
| Original label | UCI `spam`: 747; Mendeley `Spam`: 23; Mendeley `spam`: 466; Bangla `spam`: 1,806; Bangla `spam `: 249; BTTC `SPAM`: 2,684 |
| Language | `en`: 1,236; `bn`: 4,742 |
| Script | `latin`: 1,239; `bengali`: 1,439; `mixed`: 3,300 |

Length statistics: mean **209.75** characters; median **142**; minimum **6**; maximum **1,995**.

### Twenty representative review records

The following are five from each requested source grouping. They are shown as review records only;
no Sotorko label is assigned.

#### UCI spam — 5

1. `uci_sms_spam_collection / 519`: “Your credits have been topped up for http://www.bubbletext.com Your renewal Pin is...”
2. `uci_sms_spam_collection / 1595`: “PRIVATE! Your 2003 Account Statement ... Call ... Identifier Code...”
3. `uci_sms_spam_collection / 2720`: “18 days to Euro2004 kickoff! ... Unsubscribe send GET EURO STOP...”
4. `uci_sms_spam_collection / 3922`: “FREE>Ringtone! Reply REAL or POLY ... join for £3/wk”
5. `uci_sms_spam_collection / 4992`: “Phony £350 award - Todays Voda numbers ... quoting claim code...”

#### Mendeley SMS spam — 5

1. `mendeley_sms_phishing / row-000384 / Spam`: “Rediscover the deeper meaning of life ... Sms JOIN GURUBANI...”
2. `mendeley_sms_phishing / row-001769 / Spam`: “Great Investment with assured return ... Commercial space...”
3. `mendeley_sms_phishing / row-005131 / Spam`: “NON-STOP INTERNET and DOWNLOADING ... Click and play...”
4. `mendeley_sms_phishing / row-001497 / spam`: “EASTENDERS TV Quiz ... chance to WIN £100 Cash...”
5. `mendeley_sms_phishing / row-004411 / spam`: “We are specialist in placing people in BPOs ... Hiring...”

#### Bangla SMS review — 5

1. `mendeley_bangla_sms_spam_ham / row-000273 / spam`: “পবিত্র ঈদকে সামনে রেখে ... ২০% পর্যন্ত ছাড়!...”
2. `mendeley_bangla_sms_spam_ham / row-000635 / spam`: “প্রতিদিন কুরআন তিলাওয়াত সম্পন্ন করুন ...”
3. `mendeley_bangla_sms_spam_ham / row-002195 / spam`: “১৫জি.বি.+৩০০মি. ৩০দিন ৳২৪৯ রিচার্জে...”
4. `mendeley_bangla_sms_spam_ham / row-002557 / spam`: “নিশ্চিন্ত প্যাকেজে ... নতুন কলরেট...”
5. `mendeley_bangla_sms_spam_ham / row-002919 / spam`: “৪০জিবি ৩৯৮টাকা ... এয়ারটেল অ্যাপে! ...”

#### BTTC SPAM review — 5

1. `bttc_bangla / row-007506 / SPAM`: Bengali grocery promotion with a gift code and Chaldal link.
2. `bttc_bangla / row-008228 / SPAM`: bilingual agent-appointment and bank-transfer warning message.
3. `bttc_bangla / row-008826 / SPAM`: Bengali referral/commission promotion.
4. `bttc_bangla / row-009435 / SPAM`: BETJILI/JILI jackpot and gambling promotion.
5. `bttc_bangla / row-010001 / SPAM`: Bengali “free income” investment and referral promotion with a URL.

## 5. Label and domain bias

The current mapped scam class is dominated by:

- **One dataset:** 638/638 from Mendeley SMS Phishing.
- **One language:** 638/638 English.
- **One script:** 638/638 Latin.
- **Phone numbers:** 505/638, creating a strong possible shortcut feature.
- **URLs/domains:** 120/638.
- **Prize/reward language:** 162/638.
- **Payment/financial vocabulary:** 146/638.
- **Urgency:** 89/638.
- **Length:** scam mean 139.59 versus review mean 209.75 characters.

The corpus therefore risks learning source artifacts, English/Latin script, premium-rate phone
patterns, prize vocabulary, and message-length differences instead of general scam behavior. The
review corpus is mostly Bengali/Bengali-mixed, while the positive class has no Bengali examples.
This makes language and source leakage more likely than meaningful cross-lingual generalization.

## 6. Leakage-safe split design

The final split should not be performed until mapping and curation decisions are complete. Proposed
policy:

1. Group every record by exact normalized text across both JSONL files.
2. Merge groups that are identical across source IDs into one indivisible cross-source group.
3. Keep every member of each group in exactly one split; never split duplicate members across train,
   validation, and test.
4. Preserve review records in the grouping graph even though they have no label. Otherwise a text
   can appear as labeled training data and review/test context.
5. If a reliable near-duplicate method is introduced later, add its connected components to the same
   grouping graph and assign each component wholly to one split. No near-duplicate split is performed
   in this audit.
6. Assign groups using stratification only after group formation. Monitor source, language, script,
   original-label, and mapped-label distributions; do not force a split that breaks a group.
7. Keep a final isolated test group manifest and do not inspect or tune against test examples during
   development.

## 7. Additional scam-data recommendation

The current 638 mapped scam records are not enough for a useful multilingual prototype because they
are all one source, one language, one script, and one semantic family dominated by prize/premium-rate
messages. A reasonable minimum prototype target is **3,000 mapped scam records** after deduplication
and manual review, distributed across at least English, Bengali, Hindi, and Banglish, multiple
scam-category families, and multiple source types.

On that minimum target, **at least 2,362 additional scam examples** are needed. This is a planning
minimum, not a claim that the model will be production-ready. Before collecting them, the project
should define category quotas and a source-balanced curation plan; otherwise adding more examples
from the same Mendeley distribution would increase volume without reducing bias.

## Scope and reproducibility

This was a read-only audit. No labels, records, external files, API code, or model code were changed.
The calculations were performed over the current normalized and review JSONL outputs only.
