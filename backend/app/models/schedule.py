import enum
from datetime import datetime, time, date

from sqlalchemy import (
    String, Text, Boolean, DateTime, Time, Integer, Date,
    ForeignKey, Enum as SAEnum, func, JSON, UniqueConstraint
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
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


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
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    time_slot: Mapped["TimeSlot"] = relationship(back_populates="tasks")
    logs: Mapped[List["TaskLog"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class TaskLog(Base):
    """Статус выполнения задачи за конкретную дату.
    
    Task = шаблон (что делать и когда повторяется)
    TaskLog = факт (выполнил ли в этот конкретный день)
    
    Уникальность: одна запись на задачу на дату.
    """
    __tablename__ = "task_logs"
    __table_args__ = (
        UniqueConstraint("task_id", "log_date", name="uq_task_log_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    task: Mapped["Task"] = relationship(back_populates="logs")
    user: Mapped["User"] = relationship()


class DashboardSettings(Base):
    __tablename__ = "dashboard_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    visible_categories: Mapped[list] = mapped_column(JSON, default=list)
    visible_days: Mapped[list] = mapped_column(JSON, default=list)
    visible_time_slots: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="dashboard_settings")