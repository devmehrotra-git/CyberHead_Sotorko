# Sotorko Source-Label Audit

Audit date: **2026-10-07** (Asia/Calcutta)

This is a semantic audit only. Original files and original labels were not modified. Examples below are redacted report copies; `<PHONE>`, `<EMAIL>`, `<URL>`, and `<ID>` replace obvious sensitive values. No Sotorko production mapping code or normalized training data was created.

## Audit method and mapping vocabulary

Evidence was taken from source documentation stored with the downloaded files, source metadata and acquisition notes, observed records, and the source descriptions recorded locally in `docs/data-acquisition.md`.

The proposed mapping is deliberately conservative:

- `scam` — source semantics are explicitly about deceptive fraud/phishing, or a URL source explicitly labels phishing.
- `genuine` — source semantics explicitly describe legitimate/ham content.
- `excluded` — not suitable for Sotorko message-label training without a separate task or schema.
- `needs_manual_review` — source meaning is broader, ambiguous, inconsistently documented, or requires record-level evidence.

Generic `spam` is not automatically equivalent to Sotorko `scam`.

## 1. UCI SMS Spam Collection

### A–F. Labels, evidence, and proposed meaning

- **Original labels exactly as present:** `ham`, `spam`.
- **Normalized source spelling:** `ham`, `spam` (already lowercase; no whitespace variants observed).
- **Evidence:** local `readme`, which explicitly describes `ham` as legitimate and `spam` as SMS spam; observed records; 5,574 total records with `ham=4,827` and `spam=747`.

| Original label | Meaning established from source | Sotorko mapping | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `ham` | Legitimate SMS messages. | `genuine` | High | The local README explicitly says ham means legitimate. |
| `spam` | SMS spam for a general spam-filtering corpus. Examples include prizes, subscriptions, and promotional messages; the label is not defined as cyber fraud. | `needs_manual_review` | High | Generic spam is broader than Sotorko scam. Record-level fraud evidence would be required. |

### Duplicate-text audit

Grouping by exact message text while ignoring the line number found:

- 281 exact duplicate-text groups with the same label.
- 403 repeated rows belonging to those same-label groups.
- 0 exact duplicate-text groups with conflicting labels.
- 0 repeated rows in conflicting-label groups.

Therefore, repeated text is label-consistent in this source; no contradictory duplicate-label case was observed.

### Representative examples

**`ham` — five examples**

1. “Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat...”
2. “Ok lar... Joking wif u oni...”
3. “U dun say so early hor... U c already then say...”
4. “Nah I don't think he goes to usf, he lives around here though”
5. “Even my brother is not like to speak with me. They treat me like aids patent.”

**`spam` — five examples**

1. “Free entry in 2 a wkly comp to win FA Cup final tkts… Text FA to <PHONE>…”
2. “FreeMsg Hey there darling it's been 3 week's now and no word back! … £1.50 to rcv”
3. “WINNER!! As a valued network customer … receive a £900 prize reward! To claim call <PHONE>.”
4. “Had your mobile 11 months or more? … Call The Mobile Update Co FREE on <PHONE>”
5. “SIX chances to win CASH! From 100 to 20,000 pounds … Cost 150p/day…”

### Observations

The source is English-oriented and suitable as a ham/spam robustness source. `ham` is a safe candidate for genuine. `spam` should remain auxiliary or undergo manual review; it must not be bulk-mapped to scam.

## 2. SMS PHISHING DATASET FOR MACHINE LEARNING AND PATTERN RECOGNITION

### A–F. Labels, evidence, and proposed meaning

- **Original labels exactly as present:** `ham`, `Smishing`, `spam`, `Spam`, `smishing`.
- **Normalized source spelling only:** `ham`, `smishing`, `spam` after lowercasing and trimming; the case variants are not treated as distinct semantic classes.
- **Evidence:** the locally recorded Mendeley source description says the dataset contains Ham, Spam, and Smishing labels; the observed CSV has 5,971 records and fields `LABEL`, `TEXT`, `URL`, `EMAIL`, `PHONE`; examples below show the class behavior.

| Original labels | Meaning established from source and examples | Sotorko mapping | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `ham` | Legitimate/ordinary messages. | `genuine` | High | The source description calls Ham legitimate, and observed examples are ordinary conversations. |
| `Smishing`, `smishing` | SMS phishing/smishing-oriented messages, including fake alerts, prize claims, and links requesting action. | `scam` | Medium-high | The dataset title and examples explicitly identify the smishing class as phishing-oriented. |
| `spam`, `Spam` | General spam-like messages, including marketing, entertainment, offers, and some suspicious content. | `needs_manual_review` | High | The class is broader than confirmed cyber fraud and includes non-fraudulent promotional material. |

### Representative examples

**`ham` — five examples**

1. “Your opinion about me? 1. Over 2. Jada 3. Kusruthi 4. Lovable…”
2. “What's up? Do you want me to come online? If you are free we can talk sometime…”
3. “So u workin overtime nigpun?”
4. “Also sir, i sent you an email about how to log into the usc payment portal…”
5. “Sorry dude. Dont know how i forgot. Even after Dan reminded me…”

**`Smishing` — five examples**

1. “Please Stay At Home… citizens are entitled to … emergency refund. smsg.io/<URL>”
2. “BankOfAmerica Alert <ID>. Please follow <URL> re-activate”
3. “UR awarded a City Break and could WIN a £200 Summer Shopping spree…”
4. “YOU HAVE WON! As a valued Vodafone customer … win a £150 prize…”
5. “Phony £350 award … please call <PHONE> quoting claim code <ID>”

**`spam` — five examples**

1. “lyricalladie(21/F) is inviting you to be her friend. Reply YES-910 or NO-910. See her: <URL>”
2. “Hello from Orange. For 1 month's free access to games, news and sport… reply YES.”
3. “New Offer! Save upto 40% electricity bill … Rs. 1050/- … Call <PHONE>”
4. “You will recieve your tone within the next 24hrs. For Terms and conditions…”
5. “Overcome programming challenges for multicore … Attend Intel session…”

**`Spam` — five examples**

1. “Enjoy the jamster videosound gold club … get more fun from jamster.co.uk…”
2. “PL: Battle Royale! Gilchrist Vs Warne … Click <URL>…”
3. “goldviking (29/M) is inviting you to be his friend. Reply YES-762 or NO-762…”
4. “Rediscover the deeper meaning of life … Sms JOIN GURUBANI to <PHONE>”
5. “Winters & Weddings. Enjoy the season with glittering garments…”

**`smishing` — five examples**

1. “Do you want 750 anytime any network mins … call <PHONE> now…”
2. “U have a secret admirer. REVEAL who thinks U R So special. Call <PHONE>.”
3. “WIN: We have a winner! Mr. T. Tilo won an iPod! … visit <URL>”
4. “IMPORTANT INFORMATION … TODAY IS UR LUCKY DAY! … LOG ONTO <URL>”
5. “A link to your picture has been sent. You can also use <URL>”

### Ambiguity

The actual file has case variants that are likely spelling variants, not documented separate classes. The source does not provide a record-level rule that every `spam` row is fraudulent. `Smishing` is the strongest candidate for scam-oriented training, but the mapping should still be implemented through an explicit reviewed adapter rather than a case-folding-only production shortcut.

## 3. Labeled Bangla SMS Spam and Ham Dataset (2026)

### A–F. Labels, evidence, and proposed meaning

- **Original textual labels exactly as present in `spamorham`:** `ham` (1,939), `spam` (1,809), `ham ` (2), `spam ` (249).
- **Normalized source spelling only:** `ham` and `spam` after trimming trailing whitespace and lowercasing.
- **Separate numeric labels exactly as present in `label`:** `0` (1,941), `1` (2,055), and empty (3).
- **Evidence:** source title and locally recorded description identify a Bengali SMS spam/ham dataset; there is no local README defining the numeric encoding. The observed cross-tab is perfectly aligned where numeric values are present: `ham`/`ham ` maps to `0`; `spam`/`spam ` maps to `1`; three `spam` records have an empty numeric label.

| Original label | Meaning established from evidence | Sotorko mapping | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `ham`, `ham ` | Source textual ham class; observed examples are ordinary Bengali messages. | `genuine` | Medium | Dataset title and examples support legitimate meaning, but no local README was supplied. |
| `spam`, `spam ` | Source textual spam class; examples include promotions, prize claims, offers, and job claims. | `needs_manual_review` | High | Generic spam is broader than Sotorko scam. |
| `0` | Numerically aligned with ham in all 1,941 non-empty numeric-label rows. | `needs_manual_review` | Medium | Strong observed alignment, but numeric semantics are not explicitly documented locally. |
| `1` | Numerically aligned with spam in 2,055 rows. | `needs_manual_review` | Medium | Strong observed alignment, but numeric semantics are not explicitly documented locally. |
| empty numeric label | Unspecified/missing numeric annotation. | `excluded` | High | It cannot be safely interpreted. |

No mapping is made from numeric labels solely by guessing; the observed correspondence must be confirmed from the source owner or source documentation before use.

### Representative examples

Whitespace variants are shown together with their normalized spelling because the audit must preserve the exact originals while identifying likely spelling variants.

**Normalized `ham` (`ham` and `ham `) — five examples**

1. Original `ham`: “আমি বললাম না”
2. Original `ham`: “সকালে উঠে দেখি দরজা খোলা”
3. Original `ham`: “কাল দেখা হবে”
4. Original `ham `: “আমি ভাবলাম তাহলে কি”
5. Original `ham `: “আজ কি মেট্রো রেল চলে?”

**Normalized `spam` (`spam` and `spam `) — five examples**

1. Original `spam`: “আপনার মোবাইল নম্বর জিতলেন সুপার প্রাইজ! যোগাযোগ করুন: <PHONE>”
2. Original `spam`: “মোবাইল এক্সেসরিজে মেঘা ছাড়! যোগাযোগ করুন: <PHONE>”
3. Original `spam`: “আপনার সিম একটি ভালো খবর নিউজ পেতে কল করুন: <PHONE>”
4. Original `spam `: “ফ্রি টিকিট পেতে আমাদের পেইজে ভিজিট করুন।”
5. Original `spam `: “অভিনন্দন আপনি ১৫ হাজার টাকা লটারি জিতেছেন … <PHONE>”

**Numeric `0` — five examples**

1. “আমি বললাম না”
2. “সকালে উঠে দেখি দরজা খোলা”
3. “কাল দেখা হবে”
4. “আমি ভাবলাম তাহলে কি”
5. “কবে যাব?”

**Numeric `1` — five examples**

1. “আপনার মোবাইল নম্বর জিতলেন সুপার প্রাইজ! যোগাযোগ করুন: <PHONE>”
2. “মোবাইল এক্সেসরিজে মেঘা ছাড়! যোগাযোগ করুন: <PHONE>”
3. “আপনার সিম একটি ভালো খবর নিউজ পেতে কল করুন: <PHONE>”
4. “পাশবর্ধন করুন আপনার মোবাইল ডাটা প্ল্যান! যোগাযোগ করুন: <PHONE>”
5. “আপনার মোবাইল নম্বর জিতলেন সুপার প্রাইজ! যোগাযোগ করুন: <PHONE>”

**Empty numeric label — all three available examples**

1. “আড়ংয়ের ঈদ কালেকশন এখন সকল আউটলেট এবং aarong.com এ। <URL>”
2. “লম্বা ছুটিতে ঘুরতে যাওয়ার টিকেট কাটতে ক্লিক: bdtickets.com কল <PHONE>”
3. “স্বদেশপল্লীর আকর্ষণীয় ঈদ-উল-ফিতর কালেকশন … <URL>”

### Ambiguity

The missing numeric labels are on records whose textual label is `spam`; this is a data-quality issue, not evidence that the numeric encoding has a third semantic class. The numeric mapping remains `needs_manual_review` until source documentation confirms it.

## 4. BTTC Bangla Tri-class Text Corpus

### A–F. Labels, evidence, and proposed meaning

- **Original labels exactly as present:** `HAM`, `PROMO`, `SPAM`.
- **Normalized source spelling only:** `ham`, `promo`, `spam` after lowercasing.
- **Evidence:** the archive’s `Readme.txt` explicitly defines all three classes and gives their counts and examples.

| Original label | Meaning established from `Readme.txt` | Sotorko mapping | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `HAM` | Legitimate personal conversations, transactional notifications, government alerts, and public-service announcements. | `genuine` | High | The source README explicitly describes these as legitimate. |
| `PROMO` | Legitimate marketing and promotional offers, especially telecom data packs, voice minutes, and bundles. | `genuine` | High | The README separates promotional messages from malicious spam and normal ham. |
| `SPAM` | Fraudulent/phishing messages, online gambling and betting promotions, financial scams, and fake-prize offers. | `needs_manual_review` | High | The README says this class is fraud-oriented but also broader than cyber fraud. |

### Representative examples

**`HAM` — five examples**

1. “২৯ মে আন্তর্জাতিক জাতিসংঘ শান্তিরক্ষী দিবস…”
2. “৩০ জুন ২০২৫ এর মধ্যে আপনার ভূমি উন্নয়ন কর অনলাইনে land.gov.bd …”
3. “আজ ২০ মে ২০২৫, বিশ্ব মেট্রোলজি দিবস…”
4. “আপনি 60 পয়েন্ট অর্জন করেছেন। মেয়াদ: … পর্যন্ত।”
5. “আপনি ডাটা প্যাক পেয়েছেন! চেক করতে ডায়াল *৩#…”

**`PROMO` — five examples**

1. “৳২২০: ১৫ জিবি, ৩০ দিন! এখনই ডায়াল করুন *21291*2212#”
2. “আজই ২৫টাকায় ৫জিবি (সোশ্যাল প্যাক) ৩দিন নিতে ডায়াল…”
3. “আজই ৮জিবি (Social Pack) ৩দিন ৫০টাকায় কিনতে ডায়াল…”
4. “এয়ারটেলে সেরা রেট! ৪২টাকা রিচার্জে…”
5. “এয়ারটেলে ডায়ালে আজ ৬জিবি - ৳৯০…”

**`SPAM` — five examples**

1. “বাংলাদেশ নৌবাহিনীতে অফিসার ক্যাডেট পদে নিয়োগ চলছে। ভিজিট করুনঃ <URL>”
2. “৮ জিবি মাত্র ৮০ টাকায়, মেয়াদ ৭ দিন। নিতে ভিজিট: <URL>”
3. “ফ্রি! এই মাসে 50টাকা ব্যবহার করে পেয়ে যান ফ্রি ১ জিবি…”
4. “দুস্থ ও মানবতার সেবায় … বিকাশ ও নগদ <PHONE> …”
5. “বিদেশগামী শিক্ষার্থীদের … সার্টিফিকেট … আবেদন … ট্র্যাকিং নং <ID> … <URL>”

### Safe subset assessment

`SPAM` is explicitly broader than cyber fraud: it includes phishing and financial scams, but also gambling/betting promotions and other promotional or offer-like messages. The source label alone is not a safe Sotorko scam mapping. A manually reviewed subset with clear phishing, impersonation, credential theft, payment fraud, or fake-prize evidence could be mapped later; the remainder should be excluded or retained for manual review.

## 5. PhiLegit-100K phishing URL dataset

### A–F. Labels, evidence, and proposed meaning

- **Original labels exactly as present:** `0`, `1` in `label_legit_1_phish_0`.
- **Normalized source spelling only:** numeric strings `0`, `1`.
- **Evidence:** the local `README_PhiLegit-100K.md` explicitly states `1 = legitimate` and `0 = phishing`; it also states 50,000 of each and zero duplicate URLs.

| Original label | Meaning established from local README | Sotorko mapping | Confidence | Reason |
| --- | --- | --- | --- | --- |
| `0` | Phishing URL. | `scam` (URL-only) | High | Explicitly defined by the dataset README; use only in the separate URL pipeline. |
| `1` | Legitimate URL. | `genuine` (URL-only) | High | Explicitly defined by the dataset README; use only in the separate URL pipeline. |

### Representative examples

URLs are shown as redacted domain/path summaries rather than reproduced as clickable links.

**`0` — five examples**

1. `<URL domain/path: sfresim.org/login/account/clients/wait.php>`
2. `<URL domain/path: www.onetours.net>`
3. `<URL domain/path: sourit.com.cn/jp>`
4. `<URL domain/path: www.frankandmidori.com>`
5. `<URL domain/path: dev-acountbisa.pantheonsite.io/des/index.php>`

**`1` — five examples**

1. `<URL domain/path: www.hcii.cmu.edu>`
2. `<URL domain/path: www.storycenter.org>`
3. `<URL domain/path: www.udu.cas.cz>`
4. `<URL domain/path: www.snowlinehospice.org>`
5. `<URL domain/path: www.tcat.ca>`

### Suitability

The source is suitable for the separate URL model because the README explicitly defines the labels, the classes are balanced, the URLs are unique, and source-specific features are retained in `features_json`. It should not be forced into the message schema or used to create message labels.

## Proposed mapping table

| Source | Original Label | Meaning | Sotorko Mapping | Confidence | Reason |
| --- | --- | --- | --- | --- | --- |
| UCI SMS Spam | `ham` | Legitimate SMS | genuine | High | Explicit in local README. |
| UCI SMS Spam | `spam` | General SMS spam | needs_manual_review | High | Generic spam is broader than scam. |
| Mendeley SMS Phishing | `ham` | Legitimate/ordinary message | genuine | High | Source description and examples. |
| Mendeley SMS Phishing | `Smishing`, `smishing` | SMS phishing | scam | Medium-high | Title and examples are phishing-oriented. |
| Mendeley SMS Phishing | `Spam`, `spam` | General spam/marketing and mixed suspicious content | needs_manual_review | High | Not every row is a confirmed scam. |
| Bangla SMS 2026 | `ham`, `ham ` | Bengali ham | genuine | Medium | Dataset title and observed ordinary messages; no local README. |
| Bangla SMS 2026 | `spam`, `spam ` | Bengali spam | needs_manual_review | High | Generic spam is broader than scam. |
| Bangla SMS 2026 | `0` | Numerically aligned with ham | needs_manual_review | Medium | Alignment is observed, not explicitly documented. |
| Bangla SMS 2026 | `1` | Numerically aligned with spam | needs_manual_review | Medium | Alignment is observed, not explicitly documented. |
| Bangla SMS 2026 | empty numeric label | Unspecified | excluded | High | Missing source annotation. |
| BTTC | `HAM` | Legitimate personal, transactional, and public-service messages | genuine | High | Explicit in `Readme.txt`. |
| BTTC | `PROMO` | Legitimate marketing/promotional messages | genuine | High | Explicit in `Readme.txt`. |
| BTTC | `SPAM` | Fraud/phishing plus gambling, betting, and broader offer content | needs_manual_review | High | Source explicitly makes the class broader than cyber fraud. |
| PhiLegit-100K URL | `0` | Phishing URL | scam (URL-only) | High | Explicit in local README. |
| PhiLegit-100K URL | `1` | Legitimate URL | genuine (URL-only) | High | Explicit in local README. |

## Ambiguous or contradictory records

- **UCI:** No conflicting labels were found for identical message text. Duplicate text groups were label-consistent.
- **Mendeley SMS Phishing:** Case variants likely represent spelling variants, but the source does not document a separate semantic distinction. Generic `spam` contains mixed marketing and suspicious examples.
- **Bangla SMS 2026:** Three `spam` records have empty numeric labels. Numeric `0`/`1` semantics are strongly supported by cross-tab alignment but lack explicit local documentation.
- **BTTC:** `SPAM` combines phishing/fraud with gambling, betting, and other broader promotional behavior; label-only mapping is unsafe.
- **PhiLegit-100K:** No label contradiction was found. 387 URLs lack an explicit HTTP/HTTPS scheme but are generally domain/path-like rather than visibly truncated.

No changes were made to external files, production mappings, product taxonomy, API code, ML code, or rules.
