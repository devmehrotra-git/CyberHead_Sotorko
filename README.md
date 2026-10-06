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

The `POST /api/v1/analyze` endpoint is a scaffold only. Machine learning, OCR, URL analysis, scam detection, databases, authentication, frontend functionality, and external APIs are not implemented.

### Test

```bash
pytest
```
