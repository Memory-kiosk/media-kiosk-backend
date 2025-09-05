# app/routers/va.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import require_admin
from app.core.config import TOSS_SECRET_KEY, TOSS_VA_BANK
from app.services.toss_client import issue_virtual_account

router = APIRouter(tags=["payments"])

@router.post("/payments/virtual-account")
def create_va(body: dict, db: Session = Depends(get_db), _=Depends(require_admin)):
    # body: { "order_code": "...", "amount": 17000, "customer_name": "홍길동" }
    order_code = body.get("order_code"); amount = body.get("amount"); customer = body.get("customer_name")
    if not (order_code and amount and customer):
        raise HTTPException(400, "order_code, amount, customer_name required")

    payload = {
        "orderId": order_code,
        "amount": amount,
        "customerName": customer,
        "bank": TOSS_VA_BANK or "TOSSBANK",
        # 필요 시 만료/알림옵션 등 추가
    }
    va = issue_virtual_account(TOSS_SECRET_KEY, payload)
    # 응답 예: { "paymentKey": "...", "virtualAccount": { "bank":"TOSSBANK", "accountNumber":"...", "dueDate":"..." }, ... }
    # 원하면 여기서 payments 테이블에 사전 등록해둬도 됨 (paymentKey가 바로 내려오는 케이스 기준)
    return {
        "order_code": order_code,
        "bank": va.get("virtualAccount", {}).get("bank"),
        "accountNumber": va.get("virtualAccount", {}).get("accountNumber"),
        "dueDate": va.get("virtualAccount", {}).get("dueDate"),
        "paymentKey": va.get("paymentKey"),  # 응답 포함 시
    }
