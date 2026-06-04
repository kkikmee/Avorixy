export type CategoryType = 'sport' | 'daily_tasks' | 'plans'
export type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday'
export type TimeOfDay = 'morning' | 'afternoon' | 'evening' | 'night'
export type TaskStatus = 'pending' | 'in_progress' | 'done' | 'skipped'

export interface Task {
  id: number
  time_slot_id: number
  title: string
  description: string | null
  scheduled_time: string | null
  duration_minutes: number | null
  status: TaskStatus
  is_recurring: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface TimeSlot {
  id: number
  time_of_day: TimeOfDay
  is_visible: boolean
  tasks: Task[]
}

export interface DaySchedule {
  id: number
  day_of_week: DayOfWeek
  is_active: boolean
  time_slots: TimeSlot[]
}

export interface Category {
  id: number
  type: CategoryType
  title: string
  is_visible: boolean
  sort_order: number
  day_schedules: DaySchedule[]
}

export interface DashboardSettings {
  visible_categories: number[]
  visible_days: DayOfWeek[]
  visible_time_slots: TimeOfDay[]
  updated_at: string
}

export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}