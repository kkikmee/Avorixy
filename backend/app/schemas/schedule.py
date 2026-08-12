from datetime import datetime, time, date
from typing import Optional, List
from pydantic import BaseModel

from app.models.schedule import CategoryType, DayOfWeek, TimeOfDay, TaskStatus


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    is_recurring: bool = True
    sort_order: int = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    is_recurring: Optional[bool] = None
    sort_order: Optional[int] = None


class TaskRead(BaseModel):
    id: int
    time_slot_id: int
    title: str
    description: Optional[str]
    scheduled_time: Optional[time]
    duration_minutes: Optional[int]
    is_recurring: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── TaskLog ───────────────────────────────────────────────────────────────────

class TaskLogRead(BaseModel):
    id: int
    task_id: int
    user_id: int
    log_date: date
    status: TaskStatus
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskLogUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    note: Optional[str] = None


class DayLogsRead(BaseModel):
    """Все логи пользователя за один день."""
    date: str
    logs: List[TaskLogRead]


class DayStatsRead(BaseModel):
    """Статистика за день."""
    date: str
    total: int
    done: int
    skipped: int
    pending: int
    progress_pct: int


# ── TimeSlot ──────────────────────────────────────────────────────────────────

class TimeSlotCreate(BaseModel):
    time_of_day: TimeOfDay
    is_visible: bool = True


class TimeSlotRead(BaseModel):
    id: int
    time_of_day: TimeOfDay
    is_visible: bool
    tasks: List[TaskRead] = []

    model_config = {"from_attributes": True}


# ── DaySchedule ───────────────────────────────────────────────────────────────

class DayScheduleCreate(BaseModel):
    day_of_week: DayOfWeek
    is_active: bool = True


class DayScheduleRead(BaseModel):
    id: int
    day_of_week: DayOfWeek
    is_active: bool
    time_slots: List[TimeSlotRead] = []

    model_config = {"from_attributes": True}


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    type: CategoryType
    title: str
    is_visible: bool = True
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    is_visible: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryRead(BaseModel):
    id: int
    type: CategoryType
    title: str
    is_visible: bool
    sort_order: int
    day_schedules: List[DayScheduleRead] = []

    model_config = {"from_attributes": True}


# ── DashboardSettings ─────────────────────────────────────────────────────────

class DashboardSettingsUpdate(BaseModel):
    visible_categories: Optional[List[int]] = None
    visible_days: Optional[List[DayOfWeek]] = None
    visible_time_slots: Optional[List[TimeOfDay]] = None


class DashboardSettingsRead(BaseModel):
    visible_categories: List[int]
    visible_days: List[str]
    visible_time_slots: List[str]
    updated_at: datetime

    model_config = {"from_attributes": True}