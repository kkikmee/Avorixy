import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'
import type { Category, DashboardSettings, Task, TaskLog, DayStats } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  const categories = ref<Category[]>([])
  const settings = ref<DashboardSettings | null>(null)
  const loading = ref(false)

  // Логи на текущую открытую дату: Map<task_id, TaskLog>
  const logsByTaskId = ref<Map<number, TaskLog>>(new Map())
  const dayStats = ref<DayStats | null>(null)
  const currentDate = ref<string>('')

  async function fetchAll() {
    loading.value = true
    try {
      const [catsRes, settingsRes] = await Promise.all([
        api.get('/categories'),
        api.get('/dashboard/settings'),
      ])
      categories.value = catsRes.data
      settings.value = settingsRes.data
    } finally {
      loading.value = false
    }
  }

  /** Загружает логи задач за конкретную дату (YYYY-MM-DD) и обновляет статистику. */
  async function fetchDayLogs(dateStr: string) {
    currentDate.value = dateStr
    const [logsRes, statsRes] = await Promise.all([
      api.get(`/task-logs/day/${dateStr}`),
      api.get(`/task-logs/stats/${dateStr}`),
    ])
    const map = new Map<number, TaskLog>()
    for (const log of logsRes.data.logs as TaskLog[]) {
      map.set(log.task_id, log)
    }
    logsByTaskId.value = map
    dayStats.value = statsRes.data
  }

  /** Тогл статуса задачи за текущую открытую дату (pending ↔ done). */
  async function toggleTaskLog(taskId: number) {
    const dateStr = currentDate.value
    if (!dateStr) return
    const { data } = await api.post(`/task-logs/toggle/${taskId}/${dateStr}`)
    logsByTaskId.value.set(taskId, data)
    // Обновляем статистику локально, чтобы не делать лишний запрос
    await refreshStats()
  }

  async function refreshStats() {
    if (!currentDate.value) return
    const { data } = await api.get(`/task-logs/stats/${currentDate.value}`)
    dayStats.value = data
  }

  function getTaskStatus(taskId: number): string {
    return logsByTaskId.value.get(taskId)?.status ?? 'pending'
  }

  async function createCategory(type: string, title: string) {
    const { data } = await api.post('/categories', { type, title })
    categories.value.push(data)
    return data
  }

  async function deleteCategory(id: number) {
    await api.delete(`/categories/${id}`)
    categories.value = categories.value.filter((c: Category) => c.id !== id)
  }

  async function updateSettings(patch: Partial<DashboardSettings>) {
    const { data } = await api.patch('/dashboard/settings', patch)
    settings.value = data
  }

  async function createTask(slotId: number, payload: Partial<Task>) {
    const { data } = await api.post(`/tasks/slot/${slotId}`, payload)
    _injectTask(slotId, data)
    return data
  }

  async function updateTask(taskId: number, patch: Partial<Task>) {
    const { data } = await api.patch(`/tasks/${taskId}`, patch)
    _replaceTask(taskId, data)
    return data
  }

  async function deleteTask(taskId: number, slotId: number) {
    await api.delete(`/tasks/${taskId}`)
    _removeTask(slotId, taskId)
    logsByTaskId.value.delete(taskId)
  }

  function _injectTask(slotId: number, task: Task) {
    for (const cat of categories.value) {
      for (const day of cat.day_schedules) {
        const slot = day.time_slots.find(s => s.id === slotId)
        if (slot) { slot.tasks.push(task); return }
      }
    }
  }

  function _replaceTask(taskId: number, updated: Task) {
    for (const cat of categories.value) {
      for (const day of cat.day_schedules) {
        for (const slot of day.time_slots) {
          const idx = slot.tasks.findIndex(t => t.id === taskId)
          if (idx !== -1) { slot.tasks[idx] = updated; return }
        }
      }
    }
  }

  function _removeTask(slotId: number, taskId: number) {
    for (const cat of categories.value) {
      for (const day of cat.day_schedules) {
        const slot = day.time_slots.find(s => s.id === slotId)
        if (slot) { slot.tasks = slot.tasks.filter(t => t.id !== taskId); return }
      }
    }
  }

  return {
    categories, settings, loading,
    logsByTaskId, dayStats, currentDate,
    fetchAll, fetchDayLogs, toggleTaskLog, getTaskStatus, refreshStats,
    createCategory, deleteCategory, updateSettings,
    createTask, updateTask, deleteTask,
  }
})