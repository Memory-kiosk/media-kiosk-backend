# app/services/toss_client.py
import base64, httpx, os

TOSS_API_BASE = "https://api.tosspayments.com"

def _auth(secret_key: str) -> dict:
    token = base64.b64encode(f"{secret_key}:".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def issue_virtual_account(secret_key: str, payload: dict) -> dict:
    """
    payload 예시 (문서에 맞춰 조정):
    {
      "orderId": "T12-20250905-AB7Q",
      "amount": 17000,
      "customerName": "홍길동",
      "bank": "TOSSBANK",             # 원하는 은행
      "validHours": 24                # 만료
    }
    """
    headers = _auth(secret_key)
    # 실제 경로는 토스 문서에 따르세요(예: /v1/virtual-accounts 또는 /v1/payments)
    url = f"{TOSS_API_BASE}/v1/virtual-accounts"
    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
