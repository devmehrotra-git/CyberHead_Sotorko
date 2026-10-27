# Sotorko (সতর্ক) — A Bengali-First Scam Checker

**Sotorko** means “be alert” in Bengali. It is a digital-safety prototype developed by **Team CyberHead** to help users recognize suspicious messages and make safer online decisions, with an initial focus on Bengali-speaking and first-time internet users in West Bengal.

The project combines an English text-classification baseline, experimental Bengali safety rules, screenshot text extraction, and understandable safety guidance.

> **Project status:** Prototype for demonstration and evaluation. Sotorko does not guarantee that a message is safe or fraudulent. Experimental and unsupported results must be interpreted accordingly.

## 1. Problem and objective

Fraudulent messages can impersonate banks, threaten account suspension, request OTPs, demand advance fees, or use suspicious links to pressure recipients into acting quickly. Users who are less familiar with digital services may find these warning signs difficult to recognize, particularly in regional languages and mixed-script messages.

Sotorko aims to make digital-safety guidance more accessible through message analysis, visible warning indicators, and practical advice.

## 2. Current features

- **English message analysis:** Uses a saved TF-IDF and Logistic Regression baseline model.
- **Experimental English safety checks:** Detects selected credential requests, urgency, threats, and payment-related warning patterns.
- **Bengali safety checks:** Applies experimental rule-based patterns to selected suspicious Bengali messages and provides evidence in Bengali.
- **Protective-message handling:** Recognizes certain explicit English warnings against sharing credentials to avoid a known type of false alarm.
- **Screenshot text extraction:** Uses OCR to extract text from supported image uploads for the user to review.
- **Evidence and safety guidance:** Returns warning indicators and practical advice where supported by the current analysis path.
- **Automated testing:** Includes API, analyzer, OCR, frontend, reliability, and data-validation tests.
- **Multilingual evaluation:** Includes a small synthetic test set for Bengali, Banglish, Hindi, and English.

### Supported functionality and limitations

| Input or feature | Current status |
|---|---|
| English text | Saved ML baseline with selected experimental safety checks |
| Bengali text | Experimental rule-based warning signals; no calibrated risk score |
| Bengali-script auto routing | Limited heuristic routing, not general language identification |
| Banglish | Not supported by the main analysis service |
| Hindi | Not supported by the main analysis service |
| URL analysis | Not supported by the current text-message model |
| Screenshot OCR | Extracts text for review; it does not itself establish that a message is fraudulent |
| Databases, user accounts, voice assistance, and external reporting | Not implemented |

An unsupported or inconclusive response must not be interpreted as proof that a message is genuine. The Bengali rule-based component is not a trained Bengali classifier, and English model scores are not guarantees of safety or fraud.

## 3. Technology stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Request and response validation | Pydantic |
| English text classification | scikit-learn, TF-IDF, Logistic Regression |
| Bengali warning checks | Experimental Python rule-based patterns |
| Screenshot processing | Pillow, pytesseract, Tesseract OCR |
| Frontend | HTML, CSS, JavaScript served by FastAPI |
| Testing | pytest, FastAPI TestClient, httpx |
| Source control and CI | Git, GitHub Actions |

## 4. Repository structure

```text
CyberHead_Sotorko/
├── app/
│   ├── api/
│   │   └── v1/                 # Versioned API routes
│   ├── core/                   # Application configuration
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Analysis, rules, and OCR logic
│   └── main.py                 # FastAPI application entry point
├── data/
│   ├── derived/
│   │   └── ml_baseline/         # Saved English model bundle
│   └── samples/                # Example messages
├── docs/                       # Dataset and evaluation documentation
├── frontend/                   # Web interface
├── scripts/
│   ├── data/                   # Dataset inspection and validation
│   ├── evaluate_multilingual.py
│   └── ml_multilingual_experiment.py
├── tests/
│   ├── fixtures/               # Synthetic evaluation cases
│   └──                        # Automated regression tests
├── .github/workflows/           # CI workflows
├── requirements.txt
├── LICENSE
└── README.md
```

## 5. Prerequisites

- Python 3.12 is the version used in the project's GitHub Actions checks.
- Git.
- A compatible saved English model bundle at `data/derived/ml_baseline/tfidf_logistic_regression.joblib`, included in the repository.
- For screenshot OCR: a local Tesseract OCR installation, including the language data needed for the text to be extracted.

The Python dependencies are declared in `requirements.txt`.

## 6. Setup and run locally

### Windows PowerShell

Clone the repository if you do not already have a local copy:

```powershell
git clone https://github.com/devmehrotra-git/CyberHead_Sotorko.git
cd CyberHead_Sotorko
```

Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Open the following URLs in your browser:

- **Web interface:** http://127.0.0.1:8000
- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **Health endpoint:** http://127.0.0.1:8000/api/v1/health

To stop the development server, press `Ctrl+C` in the terminal.

If PowerShell blocks virtual-environment activation, you can use the environment's executable directly after creation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Linux or macOS

```bash
git clone https://github.com/devmehrotra-git/CyberHead_Sotorko.git
cd CyberHead_Sotorko

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000.

## 7. Environment variables and configuration

The current application uses fixed defaults for its application name, version, and API prefix. These do not need environment variables for a normal local run.

The analysis service supports one optional model-path environment variable:

| Variable | Required? | Purpose |
|---|---|---|
| `SOTORKO_MODEL_PATH` | No | Overrides the path to the saved English model bundle |

By default, Sotorko looks for:

```text
data/derived/ml_baseline/tfidf_logistic_regression.joblib
```

Leave `SOTORKO_MODEL_PATH` unset when using the model bundled in the repository.

### Set a custom model path in Windows PowerShell

```powershell
$env:SOTORKO_MODEL_PATH = "C:\path\to\tfidf_logistic_regression.joblib"
python -m uvicorn app.main:app --reload
```

Replace the example path with the location of a compatible model bundle.

### Set a custom model path in Linux or macOS

```bash
export SOTORKO_MODEL_PATH="/path/to/tfidf_logistic_regression.joblib"
python -m uvicorn app.main:app --reload
```

These environment-variable commands apply to the current terminal session. The variable is optional, and the default bundled model is preferred for a standard setup.

**Note:** The application does not currently require API keys, database credentials, or a `.env` file. Tesseract OCR is a separate system dependency and must be installed locally for screenshot text extraction.

## 8. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/health` | Checks that the API is responding |
| `POST` | `/api/v1/analyze` | Analyzes submitted text where the selected analysis path is supported |
| `POST` | `/api/v1/analyze/screenshot` | Extracts text from a supported image upload |

### Example text-analysis request

Use the interactive documentation at http://127.0.0.1:8000/docs, open `POST /api/v1/analyze`, and submit a request such as:

```json
{
  "input_type": "text",
  "content": "Your bank account will be blocked today. Send your OTP immediately.",
  "language": "en",
  "incident_status": "unknown"
}
```

The response contains fields such as the analysis status, verdict, optional risk score, detected language, evidence, explanation, and safety guidance.

Supported request language values include `en`, `bn`, `hi`, `banglish`, and `auto`, but accepting a language value does **not** mean that a reliable classifier is available for it. The current main analysis service does not support Hindi or Banglish classification. URL input is also unsupported.

## 9. Screenshot OCR

The endpoint `POST /api/v1/analyze/screenshot` accepts a multipart image upload in PNG, JPEG, or WebP format. It returns extracted text for review rather than treating OCR output as proof of fraud.

Current upload limits include:

- Maximum file size: 8 MB.
- Maximum image dimensions: 6000 × 6000 pixels.
- Maximum pixel count: 20 million pixels.

OCR requires the Python dependencies in `requirements.txt` and a separate local Tesseract installation. The relevant OCR language data must also be installed.

Verify the Tesseract installation from your terminal:

```powershell
tesseract --version
tesseract --list-langs
```

For English and Bengali OCR, check that `eng` and `ben` are listed.

OCR confidence describes text extraction quality only. It is **not** a scam probability. Review and correct extracted text before using it for further analysis.

The screenshot endpoint processes the uploaded image in memory and does not persist the screenshot through the application's current implementation.

## 10. Run automated tests

With the virtual environment activated, run:

```powershell
python -m pytest -q --basetemp "$PWD\.pytest-tmp-run"
```

Alternatively, from an environment where pytest's temporary directory works normally:

```bash
python -m pytest -q
```

The tests cover analysis behavior, API health, frontend behavior, OCR, backend reliability, and data validation. GitHub Actions runs the project's health check and regression suite.

A passing test suite verifies the tested behaviors; it does not establish real-world scam-detection accuracy.

## 11. Run the multilingual smoke evaluation

From the repository root:

```powershell
python scripts/evaluate_multilingual.py
```

The evaluation contains **32 synthetic examples**: four scam-labelled and four genuine-labelled messages for each of Bengali, Banglish, Hindi, and English.

The script reports the current outcomes and groups them by language. Unsupported or unavailable responses are counted as abstentions, not as successful scam detections or safe-message classifications.

The cases are illustrative and have not been independently annotated as a representative benchmark. Their results must not be used as claims of production accuracy.

The separate multilingual experiment is exploratory and is not part of the live classification service:

```powershell
python scripts/ml_multilingual_experiment.py
```

It writes exploratory artifacts under the ignored `data/derived/ml_multilingual_experiment/` directory.

## 12. Sample data and documentation

- `data/samples/sample_messages.json` — schema examples for different languages.
- `tests/fixtures/multilingual_smoke_cases.json` — synthetic multilingual evaluation cases.
- `tests/` — automated regression tests.
- `docs/dataset.md` — dataset schema and labelling guidance.
- `docs/data-sources.md` — source and provenance notes.
- `docs/multilingual-evaluation.md` — evaluation methodology and limitations.
- `docs/architecture.md` — architecture documentation.
- `scripts/data/README.md` — dataset inspection, normalization, and validation instructions.

Synthetic examples are not collected user messages and should not be represented as real-world evidence.

## 13. Dataset attribution and licensing

The English baseline is trained from a combined corpus assembled from research datasets. Their original labels and meanings are preserved in the repository's data documentation and are not automatically equivalent to Sotorko's scam/genuine labels. The combined corpus has documented source, language, duplicate, and evaluation limitations. The dataset creators and repositories do not endorse Sotorko.

Sources listed in the project's dataset attribution include:

- [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection), by Tiago Almeida and Jos Hidalgo, UCI Machine Learning Repository, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [SMS Phishing Dataset for Machine Learning and Pattern Recognition](https://data.mendeley.com/datasets/f45bkkt8pr/1), by Sandhya Mishra and Devpriya Soni, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [Labeled Bangla SMS Spam and Ham Dataset for Text Classification and Machine Learning Research](https://data.mendeley.com/datasets/hhd43jbv9p/1), by Humayet Islam, Mahazabin Rahman, Ali Hossain, Md. Rasedul Islam, Md. Ali Hossain, and Sheak Rashed Haider Noori, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [BTTC — A Bangla Tri-class Text Corpus for Spam, Ham, and Promotional Messages](https://data.mendeley.com/datasets/5wrm959d6f/1), by Labib Tahmid, Istiak Abedin, Kawsar Ahmed, Zinedin Hassan Chowdhury, and Babe Sultana, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Verify source terms and attribution before redistributing original dataset files or derived datasets. The repository's MIT license for project code does not automatically replace the licensing conditions of third-party datasets.

## 14. Privacy, safety, and limitations

Sotorko is a prototype, not a certified fraud-detection or cybersecurity product.

- A warning is an indicator to investigate, not proof of fraud.
- A message with no matched warning pattern is not necessarily safe.
- English model scores are not guarantees of safety or fraud.
- Bengali rule-based checks are experimental and may miss scams or produce false positives.
- Hindi and Banglish classification are not supported by the main analysis service.
- URL analysis, account management, databases, voice assistance, and external fraud-reporting integrations are not implemented.
- OCR output may contain transcription errors and should be reviewed.
- Do not use the prototype as the sole basis for financial or account-security decisions.

When in doubt, verify the sender through an independent official channel. Never share OTPs, PINs, passwords, or make payments solely because a message instructs you to do so.

## 15. License

The project's source code is released under the [MIT License](LICENSE). Third-party datasets and other external resources may have separate terms, attribution requirements, and redistribution restrictions.

---

**Built by Team CyberHead**  
**Project:** Sotorko (সতর্ক) — A Bengali-First Scam Checker  
**Focus:** Digital Safety & Cyber Fraud Awareness
