from app.core.db import supabase

def get_menus():
    """
    판매중인 모든 메뉴를 데이터베이스에서 조회
    """
    try:
        response = supabase.table("menu_items").select("*").eq("is_available", True).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching menus: {e}")
        return []
    
def update_menu_availability(menu_item_id: int, is_available: bool):
    '''
    특정 메뉴(menu_item_id)의 판매 기능 상태(is_available) 변경
    '''
    try:
        response = (
            supabase.table("menu_items")
            .update({"is_available": is_available})
            .eq("id", menu_item_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error updating menu availability: {e}")
        return None