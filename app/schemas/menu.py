from pydantic import BaseModel

class MenuItem(BaseModel):
    id: int
    name: str
    price: int
    is_available: bool

class MenuItemUpdate(BaseModel):
    is_available: bool
