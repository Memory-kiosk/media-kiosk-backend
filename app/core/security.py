from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.db import supabase  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

async def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    '''
    클라이언트가 보낸 Supabase JWT 토큰을 검증
    '''
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if user is None:
            raise credentials_exception
    
    except Exception:
        raise credentials_exception
    return user