# Sotorko (সতর্ক)

Sotorko means “be alert.” It is a vernacular digital-safety companion being built by Team CyberHead for the VBYLD 2027 Hack for Social Cause competition.

## Initial backend

This project contains an initial Python, FastAPI, and Pydantic backend scaffold.

### Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available under `/api/v1`. The health check is `GET /api/v1/health`, and interactive documentation is available at `/docs`.

## Dataset attribution

The English baseline is trained from a combined corpus assembled from the following
research datasets. Their source labels and meanings are preserved in the repository's
data documentation; they are not automatically equivalent to Sotorko scam/genuine
labels, and the combined corpus has documented source, language, duplicate, and
evaluation limitations. The dataset creators and repositories do not endorse Sotorko.

- [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection), by Tiago Almeida and Jos Hidalgo, UCI Machine Learning Repository, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [SMS Phishing Dataset for Machine Learning and Pattern Recognition](https://data.mendeley.com/datasets/f45bkkt8pr/1), by Sandhya Mishra and Devpriya Soni, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [Labeled Bangla SMS Spam and Ham Dataset for Text Classification and Machine Learning Research](https://data.mendeley.com/datasets/hhd43jbv9p/1), by Humayet Islam, Mahazabin Rahman, Ali Hossain, Md. Rasedul Islam, Md. Ali Hossain, and Sheak Rashed Haider Noori, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [BTTC — A Bangla Tri-class Text Corpus for Spam, Ham, and Promotional Messages](https://data.mendeley.com/datasets/5wrm959d6f/1), by Labib Tahmid, Istiak Abedin, Kawsar Ahmed, Zinedin Hassan Chowdhury, and Babe Sultana, Mendeley Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Attribution and licensing claims should still be rechecked against the source pages
before redistributing source payloads or derived data.

The `POST /api/v1/analyze` endpoint uses the saved English TF-IDF + Logistic Regression baseline for explicit English text input. Explicit Bengali input uses a separate, narrow experimental rule-based signal that can report evidence-backed warnings but has no calibrated risk score and must not be treated as a trained Bengali classifier. Banglish, Hindi, auto-detected language, and URL analysis remain explicitly unsupported. English model scores are not guarantees of safety or fraud.

### Screenshot OCR

`POST /api/v1/analyze/screenshot` accepts a multipart PNG, JPEG, or WebP upload and
returns extracted text for user review. The screenshot is processed in memory and is
not persisted by the application. The endpoint enforces an 8 MB file limit, maximum
dimensions of 6000×6000 pixels, and a 20-million-pixel limit.

OCR requires both the Python dependencies in `requirements.txt` (`Pillow` and
`pytesseract`) and a local Tesseract installation. The Python wrapper alone is not
enough. Add the `eng` language data for English and `ben` language data for Bengali,
then verify from a project terminal:

```powershell
tesseract --version
tesseract --list-langs
pip install -r requirements.txt
```

The verified development environment includes the Tesseract executable, English and
Bengali language data, and the OCR Python packages, so English and Bengali screenshot
extraction are available locally. OCR confidence describes text extraction only;
it is never a scam-detection confidence. Users must review and correct extracted text
before sending it to the analyzer.

The multilingual experiment is separate from production:

```powershell
.\.venv\Scripts\python.exe scripts/ml_multilingual_experiment.py
```

It excludes uncertain annotations and writes exploratory artifacts under the ignored
`data/derived/ml_multilingual_experiment/`. The live Bengali path is experimental rules
only; Bengali ML classification and Banglish classification remain unsupported until
each has independent human-verified scam and genuine test coverage. Databases,
authentication, voice assistance, URL analysis, and external APIs are not implemented.

### Test

```bash
pytest
```
