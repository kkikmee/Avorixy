from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.schedule import DashboardSettings
from app.schemas.schedule import DashboardSettingsUpdate, DashboardSettingsRead
from app.core.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/settings", response_model=DashboardSettingsRead)
async def get_settings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(DashboardSettings).where(DashboardSettings.user_id == current_user.id))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")
    return settings

@router.patch("/settings", response_model=DashboardSettingsRead)
async def update_settings(payload: DashboardSettingsUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(DashboardSettings).where(DashboardSettings.user_id == current_user.id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = DashboardSettings(user_id=current_user.id)
        db.add(settings)
    data = payload.model_dump(exclude_unset=True)
    if "visible_days" in data and data["visible_days"] is not None:
        data["visible_days"] = [d.value if hasattr(d, "value") else d for d in data["visible_days"]]
    if "visible_time_slots" in data and data["visible_time_slots"] is not None:
        data["visible_time_slots"] = [s.value if hasattr(s, "value") else s for s in data["visible_time_slots"]]
    for field, value in data.items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings