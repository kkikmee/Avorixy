from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.schedule import DashboardSettings
from app.schemas.user import UserCreate, UserRead, UserUpdate, TokenResponse, RefreshRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where((User.email == payload.email) | (User.username == payload.username)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email или username уже занят")
    user = User(email=payload.email, username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.flush()
    settings = DashboardSettings(user_id=user.id, visible_categories=[], visible_days=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], visible_time_slots=["morning","afternoon","evening","night"])
    db.add(settings)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")
    return TokenResponse(access_token=create_access_token({"sub": str(user.id)}), refresh_token=create_refresh_token({"sub": str(user.id)}))

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный тип токена")
    result = await db.execute(select(User).where(User.id == int(data["sub"])))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return TokenResponse(access_token=create_access_token({"sub": str(user.id)}), refresh_token=create_refresh_token({"sub": str(user.id)}))

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user