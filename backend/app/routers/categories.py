from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.schedule import Category, DaySchedule, TimeSlot, DayOfWeek, TimeOfDay
from app.schemas.schedule import CategoryCreate, CategoryUpdate, CategoryRead
from app.core.security import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])
ALL_DAYS = list(DayOfWeek)
ALL_SLOTS = list(TimeOfDay)

def load_full(query):
    return query.options(selectinload(Category.day_schedules).selectinload(DaySchedule.time_slots).selectinload(TimeSlot.tasks))

@router.get("", response_model=List[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(load_full(select(Category).where(Category.user_id == current_user.id).order_by(Category.sort_order)))
    return result.scalars().all()

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = Category(user_id=current_user.id, type=payload.type, title=payload.title, is_visible=payload.is_visible, sort_order=payload.sort_order)
    db.add(category)
    await db.flush()
    for day in ALL_DAYS:
        day_schedule = DaySchedule(category_id=category.id, day_of_week=day)
        db.add(day_schedule)
        await db.flush()
        for slot in ALL_SLOTS:
            db.add(TimeSlot(day_schedule_id=day_schedule.id, time_of_day=slot))
    await db.commit()
    result = await db.execute(load_full(select(Category).where(Category.id == category.id)))
    return result.scalar_one()

@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: int, payload: CategoryUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(load_full(select(Category).where(Category.id == category_id, Category.user_id == current_user.id)))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.user_id == current_user.id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await db.delete(category)
    await db.commit()