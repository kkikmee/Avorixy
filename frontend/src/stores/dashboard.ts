import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'
import type { Category, DashboardSettings, Task } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  const categories = ref<Category[]>([])
  const settings = ref<DashboardSettings | null>(null)
  const loading = ref(false)

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
  }

  async function setTaskStatus(taskId: number, status: string) {
    const { data } = await api.patch(`/tasks/${taskId}/status?new_status=${status}`)
    _replaceTask(taskId, data)
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
    fetchAll, createCategory, deleteCategory, updateSettings,
    createTask, updateTask, deleteTask, setTaskStatus,
  }
})