from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse, PasswordChange
from app.models.user import User
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repo = UserRepository(db)
    updated = await user_repo.update(current_user.id, data.model_dump(exclude_unset=True))
    return UserResponse.model_validate(updated)


@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user_repo = UserRepository(db)
    await user_repo.update(current_user.id, {"hashed_password": get_password_hash(data.new_password)})
    return {"message": "Password changed successfully"}


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(refresh_token)
