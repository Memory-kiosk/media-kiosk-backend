import random
import string
from app.core.db import supabase
from app.schemas.orders import OrderCreate

# 간단한 주문 코드 생성 함수
def generate_order_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_order(order_data: OrderCreate):
    # --- 💡 1. 테이블 ID 조회 로직 추가 ---
    try:
        table_response = supabase.table("tables").select("id").eq("table_no", order_data.table_no).single().execute()
        table_id = table_response.data['id']
    except Exception as e:
        # 해당하는 테이블 번호가 DB에 없을 경우
        print(f"Error finding table_no: {order_data.table_no}. Error: {e}")
        return {"error": f"Table number {order_data.table_no} does not exist."}

    # 2. 프론트에서 받은 메뉴 ID 목록 추출
    menu_item_ids = [item.menu_item_id for item in order_data.items]
    
    # 3. DB에서 해당 메뉴들의 정보(가격, 판매 가능 여부)를 한 번에 조회
    try:
        menu_response = supabase.table("menu_items").select("id, price, is_available").in_("id", menu_item_ids).execute()
        menu_items_db = menu_response.data
    except Exception as e:
        print(f"Error fetching menu items from DB: {e}")
        return None

    # 4. 데이터 검증 및 총액 계산
    menu_price_map = {item['id']: {"price": item['price'], "is_available": item['is_available']} for item in menu_items_db}
    
    total_amount = 0
    order_items_to_create = []

    for item in order_data.items:
        menu_id = item.menu_item_id
        if menu_id not in menu_price_map or not menu_price_map[menu_id]['is_available']:
            return {"error": f"Menu item {menu_id} is not available or does not exist."}
        
        price = menu_price_map[menu_id]['price']
        total_amount += price * item.qty
        
        order_items_to_create.append({
            "menu_item_id": menu_id,
            "qty": item.qty,
            "price_unit": price
        })

    # 5. `orders` 테이블에 주문 정보 저장
    try:
        new_order_data = {
            "table_id": table_id,  # <--- 💡 2. 'table_no'를 조회해온 'table_id'로 변경
            "customer_name": order_data.customer_name,
            "order_code": generate_order_code(),
            "amount_total": total_amount,
        }
        order_response = supabase.table("orders").insert(new_order_data).execute()
        created_order = order_response.data[0]
        new_order_id = created_order['id']

    except Exception as e:
        print(f"Error creating order: {e}")
        return {"error": "Could not create an order."}

    # 6. `order_items` 테이블에 주문 항목들 저장
    for item in order_items_to_create:
        item['order_id'] = new_order_id

    try:
        supabase.table("order_items").insert(order_items_to_create).execute()
    except Exception as e:
        print(f"Error creating order items, but order was created (ID: {new_order_id}): {e}")
        return {"error": "Could not create order items."}

    # 7. 성공적으로 생성된 주문 정보 반환
    # API 응답에는 table_id 대신 table_no를 다시 넣어주면 더 친절합니다.
    created_order['table_no'] = order_data.table_no
    return created_order