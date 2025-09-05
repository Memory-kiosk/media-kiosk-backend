# app/routers/payments_toss.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import require_admin  # 웹훅엔 보통 미적용. 대신 Basic 서명 검증 권장
from app.core.config import TOSS_WEBHOOK_BASIC
from app.models.entities import Order, PaymentStatus, OrderStatus
from loguru import logger

router = APIRouter(tags=["payments"])

def _verify_webhook_auth(req: Request):
    if not TOSS_WEBHOOK_BASIC:
        return True
    auth = req.headers.get("Authorization", "")
    if auth != f"Basic {TOSS_WEBHOOK_BASIC}":
        raise HTTPException(401, "invalid webhook auth")

@router.post("/payments/toss/callback")
async def toss_callback(req: Request, db: Session = Depends(get_db)):
    _verify_webhook_auth(req)
    payload = await req.json()
    logger.info(f"Toss webhook: {payload}")

    # 중요 필드(문서에 맞게 조정)
    payment_key = payload.get("paymentKey")
    order_id    = payload.get("orderId")
    status      = payload.get("status")             # WAITING_FOR_DEPOSIT / DONE / CANCELED ...
    amount      = payload.get("totalAmount") or payload.get("amount")

    # 멱등: 거래(transactionKey) 기준으로 payment_transactions에 insert on conflict do nothing
    tx_key = payload.get("transactionKey") or payload.get("eventKey") or payment_key
    db.execute("""
        insert into public.payment_transactions (payment_key, transaction_key, status, amount, transaction_at, raw)
        values (:payment_key, :transaction_key, :status, :amount, now(), :raw)
        on conflict (transaction_key) do nothing
    """, dict(payment_key=payment_key, transaction_key=tx_key, status=status, amount=amount, raw=payload))

    # payments upsert (paymentKey 기준)
    db.execute("""
        insert into public.payments (payment_key, order_code, method, amount, status, receipt_url)
        values (:payment_key, :order_code, :method, :amount, :status, :receipt_url)
        on conflict (payment_key) do update set
          order_code=excluded.order_code,
          method=excluded.method,
          amount=excluded.amount,
          status=excluded.status,
          receipt_url=excluded.receipt_url
    """, dict(
        payment_key=payment_key,
        order_code=order_id,
        method=payload.get("method", "virtual-account"),
        amount=amount,
        status=status,
        receipt_url=payload.get("receiptUrl"),
    ))

    # 주문 매칭 + 상태 반영
    if order_id:
        order = db.query(Order).filter(Order.order_code == order_id).one_or_none()
        if order:
            if status == "DONE":
                if amount == order.amount_total:
                    order.payment_status = PaymentStatus.paid
                    if order.order_status == OrderStatus.pending:
                        order.order_status = OrderStatus.accepted
                else:
                    # 금액 불일치 - 별도 정책
                    logger.warning(f"Amount mismatch for {order_id}: va={amount}, order={order.amount_total}")
            elif status in ("CANCELED", "PARTIAL_CANCELED"):
                order.payment_status = PaymentStatus.failed
            db.add(order)

    db.commit()
    return {"ok": True}
