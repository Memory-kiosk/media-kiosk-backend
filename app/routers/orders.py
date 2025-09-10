from fastapi import APIRouter, HTTPException, status
from app.services import orders_service
from app.schemas.orders import OrderCreate, Order

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_new_order(order_data: OrderCreate):
    '''
    새로운 주문을 생성하는 API
    - table_no, customer_name, items 목록을 받아 주문을 생성
    - 성공 시 생성도니 주문 정보를 반환
    '''
    created_order = orders_service.create_order(order_data)

    if not created_order:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "내부 오류로 인해 주문을 처리할 수 없습니다~"
        )
    if created_order.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=created_order["error"]
        )
    
    return created_order