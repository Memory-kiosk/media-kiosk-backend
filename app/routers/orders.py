from fastapi import APIRouter, HTTPException, status
from app.services import orders_service
from app.schemas.orders import OrderCreate, Order

from typing import List

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

@router.get("", response_model=List[Order])
def read_orders(status: str = 'pending'):
    '''
    특정 상태의 주문 목록을 조회하는 API
    - 쿼리 파라미터로 status를 받으며, 기본값은 'pending'임
    '''
    orders_data = orders_service.get_orders(status=status)

    # Supabase 조인 결과는 {'id': 1, ..., 'tables': {'table_no': 5}} 와 같이 중첩되어 있습니다.
    # 이를 {'id': 1, ..., 'table_no': 5} 형태로 변환해줍니다.

    for order in orders_data:
        if 'tables' in order and order['tables'] is not None:
            order['table_no'] = order['tables']['table_no']
        else:
            order['table_no'] = -1

        del order['tables']
    return orders_data