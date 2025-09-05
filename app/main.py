import os, base64, httpx
from fastapi import FastAPI

TOSS_API_BASE = "https://api.tosspayments.com"
SECRET_KEY = os.getenv("TOSS_SECRET_KEY")

app = FastAPI()

def _auth_header(secret_key: str) -> dict:
    token = base64.b64encode(f"{secret_key}:".encode()).decode()
    return {"Authorization": f"Basic {token}"}

@app.get("/test/toss")
def test_toss():
    """토스 거래조회 API 호출이 되는지만 확인"""
    headers = _auth_header(SECRET_KEY)
    params = {
        "startDate": "2025-09-01T00:00:00",
        "endDate":   "2025-09-05T23:59:59",
        "limit": 1
    }
    with httpx.Client(timeout=65.0) as client:
        r = client.get(f"{TOSS_API_BASE}/v1/transactions", headers=headers, params=params)
        try:
            r.raise_for_status()
        except Exception as e:
            return {"ok": False, "error": str(e), "body": r.text}
        return {"ok": True, "status": r.status_code, "body": r.json()}
