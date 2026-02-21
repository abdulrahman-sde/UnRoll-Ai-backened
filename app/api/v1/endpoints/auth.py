from fastapi import APIRouter, Depends, status

from app.schemas.user import UserLogin, UserRegister
from app.services.auth_service import AuthService, get_auth_service
from app.utils.utils import success_response

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(register_data)
    return success_response("User created successfully", data=user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.login(credentials)
    return success_response("User logged in successfully", data=user)

