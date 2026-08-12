from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.schedule import Task, TimeSlot, DaySchedule, Category
from app.schemas.schedule import TaskCreate, TaskUpdate, TaskRead
from app.core.security import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

async def _get_slot_for_user(slot_id: int, user: User, db: AsyncSession) -> TimeSlot:
    result = await db.execute(select(TimeSlot).join(DaySchedule).join(Category).where(TimeSlot.id == slot_id, Category.user_id == user.id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="TimeSlot не найден")
    return slot

@router.get("/slot/{slot_id}", response_model=List[TaskRead])
async def list_tasks_by_slot(slot_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await _get_slot_for_user(slot_id, current_user, db)
    result = await db.execute(select(Task).where(Task.time_slot_id == slot_id).order_by(Task.sort_order, Task.scheduled_time))
    return result.scalars().all()

@router.post("/slot/{slot_id}", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(slot_id: int, payload: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await _get_slot_for_user(slot_id, current_user, db)
    task = Task(time_slot_id=slot_id, **payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).join(TimeSlot).join(DaySchedule).join(Category).where(Task.id == task_id, Category.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).join(TimeSlot).join(DaySchedule).join(Category).where(Task.id == task_id, Category.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await db.delete(task)
    await db.commit()