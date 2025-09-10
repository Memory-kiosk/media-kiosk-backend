from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services import menu_service
from app.schemas.menu import MenuItem, MenuItemUpdate
from app.core.security import get_current_admin_user

router = APIRouter()

@router.get("", response_model = List[MenuItem])
def read_menus():
    '''
    판매 중인 모든 메뉴 목록을 조회하는 API
    '''
    menus = menu_service.get_menus()
    return menus

@router.patch("/{menu_item_id}", dependencies=[Depends(get_current_admin_user)])
def update_menu_item_status(menu_item_id: int, menu_data: MenuItemUpdate):
    '''
    특정 메뉴의 판매 기능 상태를 변경하는 API, 관리자 전용
    is_available 값을 true or false로 변경
    '''
    updated_menu = menu_service.update_menu_availability(
        menu_item_id = menu_item_id, is_available = menu_data.is_available
    )

    if not updated_menu:
        raise HTTPException(
            status_code = 404,
            detail=f"Menu item with ID {menu_item_id} not found"
        )
    
    return {"message" : f"Menu item {menu_item_id} status updated succesfully"}