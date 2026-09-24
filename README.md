# SentinelAPI

SentinelAPI is a local, authorization-aware API vulnerability scanner demo. It includes a deliberately vulnerable FastAPI target and a FastAPI scanner UI/API. The project is intended for authorized testing of targets explicitly supplied for a scan session.

## Run with Docker Compose

```bash
docker compose up --build
```

Open http://localhost:8000. The New Scan form is pre-filled with the demo target OpenAPI URL (`http://demo-target:8001/openapi.json`) and target (`http://demo-target:8001`). Use these demo credentials:

```json
{"userA":"token-a","userB":"token-b"}
```

Check all four check classes, confirm authorization, and start the scan. The seeded demo should produce BOLA, sensitive-data exposure, missing-auth, and rate-limit findings.

## Local fallback without Docker

If Docker is unavailable, run two terminals:

```bash
cd demo_target && python3 -m pip install -r requirements.txt  # or install fastapi/uvicorn
uvicorn main:app --host 127.0.0.1 --port 8001

cd backend && pip install -r requirements.txt
DATABASE_PATH=../data/sentinelapi.db uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For local fallback, use `http://127.0.0.1:8001/openapi.json` and `http://127.0.0.1:8001` in the form.

## Safety boundary

The scanner never crawls or discovers hosts. It only makes requests to the exact target base URL and spec URL supplied in the scan record. Every scan requires an explicit authorization confirmation, which is stored with the scan.
