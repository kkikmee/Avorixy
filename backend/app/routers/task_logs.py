from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.models.schedule import (
    Task, TaskLog, TaskStatus, TimeSlot, DaySchedule, Category, DayOfWeek
)
from app.schemas.schedule import TaskLogRead, TaskLogUpdate, DayLogsRead, DayStatsRead
from app.core.security import get_current_user

router = APIRouter(prefix="/api/task-logs", tags=["task-logs"])

# Python weekday() → DayOfWeek (0=Monday)
WEEKDAY_MAP = {
    0: DayOfWeek.MONDAY,
    1: DayOfWeek.TUESDAY,
    2: DayOfWeek.WEDNESDAY,
    3: DayOfWeek.THURSDAY,
    4: DayOfWeek.FRIDAY,
    5: DayOfWeek.SATURDAY,
    6: DayOfWeek.SUNDAY,
}


def parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используй YYYY-MM-DD")


async def get_or_create_log(
    task_id: int,
    user_id: int,
    log_date: date,
    db: AsyncSession,
) -> TaskLog:
    """Получаем лог за дату, если нет — создаём со статусом pending."""
    result = await db.execute(
        select(TaskLog).where(
            and_(
                TaskLog.task_id == task_id,
                TaskLog.user_id == user_id,
                TaskLog.log_date == log_date,
            )
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        log = TaskLog(
            task_id=task_id,
            user_id=user_id,
            log_date=log_date,
            status=TaskStatus.PENDING,
        )
        db.add(log)
        await db.flush()
    return log


@router.get("/day/{date_str}", response_model=DayLogsRead)
async def get_day_logs(
    date_str: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает все логи за день.
    Для задач у которых нет лога — создаёт pending автоматически.
    """
    log_date = parse_date(date_str)
    day_of_week = WEEKDAY_MAP[log_date.weekday()]

    # Все задачи пользователя на этот день недели
    result = await db.execute(
        select(Task)
        .join(TimeSlot)
        .join(DaySchedule)
        .join(Category)
        .where(
            and_(
                Category.user_id == current_user.id,
                DaySchedule.day_of_week == day_of_week,
                DaySchedule.is_active == True,
            )
        )
    )
    tasks = result.scalars().all()

    logs = []
    for task in tasks:
        log = await get_or_create_log(task.id, current_user.id, log_date, db)
        logs.append(log)

    await db.commit()
    return DayLogsRead(date=date_str, logs=logs)


@router.post("/toggle/{task_id}/{date_str}", response_model=TaskLogRead)
async def toggle_task_log(
    task_id: int,
    date_str: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Тогл задачи: pending → done → pending.
    Вызывается при клике на чекбокс в UI.
    """
    # Проверяем что задача принадлежит пользователю
    result = await db.execute(
        select(Task)
        .join(TimeSlot)
        .join(DaySchedule)
        .join(Category)
        .where(and_(Task.id == task_id, Category.user_id == current_user.id))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Задача не найдена")

    log_date = parse_date(date_str)
    log = await get_or_create_log(task_id, current_user.id, log_date, db)

    log.status = TaskStatus.DONE if log.status != TaskStatus.DONE else TaskStatus.PENDING

    await db.commit()
    await db.refresh(log)
    return log


@router.patch("/{log_id}", response_model=TaskLogRead)
async def update_log(
    log_id: int,
    payload: TaskLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить статус или заметку конкретного лога."""
    result = await db.execute(
        select(TaskLog).where(
            and_(TaskLog.id == log_id, TaskLog.user_id == current_user.id)
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Лог не найден")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)
    return log


@router.get("/stats/{date_str}", response_model=DayStatsRead)
async def get_day_stats(
    date_str: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Статистика за день: всего, выполнено, пропущено, процент."""
    log_date = parse_date(date_str)

    result = await db.execute(
        select(TaskLog).where(
            and_(
                TaskLog.user_id == current_user.id,
                TaskLog.log_date == log_date,
            )
        )
    )
    logs = result.scalars().all()

    total = len(logs)
    done = sum(1 for l in logs if l.status == TaskStatus.DONE)
    skipped = sum(1 for l in logs if l.status == TaskStatus.SKIPPED)

    return DayStatsRead(
        date=date_str,
        total=total,
        done=done,
        skipped=skipped,
        pending=total - done - skipped,
        progress_pct=round((done / total * 100) if total > 0 else 0),
    )