import enum
from datetime import datetime, time

from sqlalchemy import (
    String, Text, Boolean, DateTime, Time, Integer,
    ForeignKey, Enum as SAEnum, func, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.database import Base


class CategoryType(str, enum.Enum):
    SPORT = "sport"
    DAILY_TASKS = "daily_tasks"
    PLANS = "plans"


class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TimeOfDay(str, enum.Enum):
    MORNING = "morning"    # 06:00 – 12:00
    AFTERNOON = "afternoon"  # 12:00 – 18:00
    EVENING = "evening"    # 18:00 – 23:00
    NIGHT = "night"        # 23:00 – 06:00


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[CategoryType] = mapped_column(SAEnum(CategoryType), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="categories")
    day_schedules: Mapped[List["DaySchedule"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class DaySchedule(Base):
    """Один день недели внутри категории."""
    __tablename__ = "day_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(SAEnum(DayOfWeek), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["Category"] = relationship(back_populates="day_schedules")
    time_slots: Mapped[List["TimeSlot"]] = relationship(
        back_populates="day_schedule", cascade="all, delete-orphan"
    )


class TimeSlot(Base):
    """Блок времени суток внутри дня: утро/день/вечер/ночь."""
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    day_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("day_schedules.id", ondelete="CASCADE"), index=True
    )
    time_of_day: Mapped[TimeOfDay] = mapped_column(SAEnum(TimeOfDay), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)

    day_schedule: Mapped["DaySchedule"] = relationship(back_populates="time_slots")
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="time_slot", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    time_slot_id: Mapped[int] = mapped_column(
        ForeignKey("time_slots.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.PENDING
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    time_slot: Mapped["TimeSlot"] = relationship(back_populates="tasks")


class DashboardSettings(Base):
    """Настройки dashboard конкретного пользователя — что показывать."""
    __tablename__ = "dashboard_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    # JSON: { "visible_categories": [1,2], "visible_days": ["monday","tuesday"], "visible_time_slots": ["morning","evening"] }
    visible_categories: Mapped[list] = mapped_column(JSON, default=list)
    visible_days: Mapped[list] = mapped_column(JSON, default=list)
    visible_time_slots: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="dashboard_settings")