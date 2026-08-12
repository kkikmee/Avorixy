<template>
  <div class="app-layout">
    <AppSidebar :active-category-id="activeCategoryId" @select-category="selectCategory" @add-category="showAddCategory = true" />

    <div class="main">
      <AppHeader />

      <div class="content">
        <!-- Day selector -->
        <div class="day-bar">
          <div class="day-bar-left">
            <h2 class="day-title">{{ currentDayLabel }} <span class="day-chevron">▾</span></h2>
          </div>
          <div class="day-bar-right">
            <button class="day-nav" @click="shiftWeek(-1)">‹</button>
            <div class="days-row">
              <button
                v-for="d in weekDays"
                :key="d.iso"
                class="day-btn"
                :class="{ 'day-btn--active': selectedDate === d.iso }"
                @click="selectDate(d.iso)"
              >
                <span class="day-label">{{ d.short }}</span>
                <span class="day-num">{{ d.num }}</span>
              </button>
            </div>
            <button class="day-nav" @click="shiftWeek(1)">›</button>
            <button class="today-btn" @click="goToday">Today</button>
          </div>
        </div>

        <!-- Category tabs -->
        <div class="cat-tabs">
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="cat-tab"
            :class="{ 'cat-tab--active': activeCategoryId === cat.id }"
            @click="selectCategory(cat.id)"
          >
            {{ getCategoryIcon(cat.type) }} {{ cat.title }}
          </button>
          <button class="cat-tab cat-tab--add" @click="showAddCategory = true">＋</button>
        </div>

        <!-- Time slot columns -->
        <div v-if="activeCategory" class="slots-grid">
          <div v-for="slot in currentDaySlots" :key="slot.id" class="slot-col">
            <div class="slot-header">
              <span class="slot-icon">{{ getSlotIcon(slot.time_of_day) }}</span>
              <div>
                <p class="slot-title">{{ getSlotLabel(slot.time_of_day) }}</p>
                <p class="slot-time">{{ getSlotTime(slot.time_of_day) }}</p>
              </div>
            </div>

            <div class="slot-tasks">
              <div v-for="task in slot.tasks" :key="task.id" class="task-item">
                <button
                  class="task-check"
                  :class="{ 'task-check--done': dash.getTaskStatus(task.id) === 'done' }"
                  @click="dash.toggleTaskLog(task.id)"
                >
                  <svg v-if="dash.getTaskStatus(task.id) === 'done'" width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>
                </button>
                <span class="task-title" :class="{ 'task-done': dash.getTaskStatus(task.id) === 'done' }">{{ task.title }}</span>
                <span v-if="task.scheduled_time" class="task-time">{{ task.scheduled_time.slice(0, 5) }}</span>
              </div>

              <button class="task-add" @click="openAddTask(slot.id)">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
                Add task
              </button>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else-if="!dash.loading" class="empty-state">
          <p>Создай первую категорию чтобы начать</p>
          <button class="btn-primary-sm" @click="showAddCategory = true">+ Добавить категорию</button>
        </div>
      </div>
    </div>

    <!-- Right panel -->
    <aside class="right-panel">
      <DailyOverview />
    </aside>

    <!-- Add category modal -->
    <div v-if="showAddCategory" class="modal-overlay" @click.self="showAddCategory = false">
      <div class="modal">
        <h3 class="modal-title">Новая категория</h3>
        <div class="field">
          <label>Тип</label>
          <select v-model="newCatType" class="select">
            <option value="sport">💪 Спорт</option>
            <option value="daily_tasks">✅ Задачи</option>
            <option value="plans">🎯 Планы</option>
          </select>
        </div>
        <div class="field">
          <label>Название</label>
          <input v-model="newCatTitle" class="input" placeholder="Название категории" />
        </div>
        <div class="modal-actions">
          <button class="btn-ghost" @click="showAddCategory = false">Отмена</button>
          <button class="btn-primary-sm" @click="addCategory">Создать</button>
        </div>
      </div>
    </div>

    <!-- Add task modal -->
    <div v-if="addTaskSlotId !== null" class="modal-overlay" @click.self="addTaskSlotId = null">
      <div class="modal">
        <h3 class="modal-title">Новая задача</h3>
        <div class="field">
          <label>Название</label>
          <input v-model="newTaskTitle" class="input" placeholder="Что нужно сделать?" @keyup.enter="saveTask" />
        </div>
        <div class="field">
          <label>Время (необязательно)</label>
          <input v-model="newTaskTime" class="input" type="time" />
        </div>
        <div class="field">
          <label class="checkbox-label">
            <input v-model="newTaskRecurring" type="checkbox" />
            Повторять каждую неделю в этот день
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn-ghost" @click="addTaskSlotId = null">Отмена</button>
          <button class="btn-primary-sm" @click="saveTask">Добавить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import DailyOverview from '@/components/widgets/DailyOverview.vue'
import { useDashboardStore } from '@/stores/dashboard'
import type { Task } from '@/types'

const dash = useDashboardStore()
const categories = computed(() => dash.categories)
const activeCategoryId = ref<number | null>(null)
const weekOffset = ref(0)
const selectedDate = ref<string>('')   // ISO "2025-06-04"

const showAddCategory = ref(false)
const newCatType = ref('daily_tasks')
const newCatTitle = ref('')
const addTaskSlotId = ref<number | null>(null)
const newTaskTitle = ref('')
const newTaskTime = ref('')
const newTaskRecurring = ref(true)

const DAY_KEYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
const DAY_SHORT = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']

function toISO(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// Понедельник той недели, что смещена на weekOffset недель от сегодня
function mondayOfWeek(offset: number): Date {
  const today = new Date()
  const dow = today.getDay() === 0 ? 7 : today.getDay() // 1..7, Пн=1
  const monday = new Date(today)
  monday.setDate(today.getDate() - (dow - 1) + offset * 7)
  return monday
}

const weekDays = computed(() => {
  const monday = mondayOfWeek(weekOffset.value)
  return DAY_KEYS.map((key, i) => {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    return { key, short: DAY_SHORT[i], num: date.getDate(), iso: toISO(date), dateObj: date }
  })
})

const selectedDayKey = computed(() => {
  const found = weekDays.value.find(d => d.iso === selectedDate.value)
  return found?.key ?? 'monday'
})

const currentDayLabel = computed(() => {
  const d = weekDays.value.find(d => d.iso === selectedDate.value)
  if (!d) return ''
  const fullName = d.key.charAt(0).toUpperCase() + d.key.slice(1)
  return `${fullName}, ${MONTHS[d.dateObj.getMonth()]} ${d.num}`
})

function shiftWeek(dir: number) { weekOffset.value += dir }

function goToday() {
  weekOffset.value = 0
  selectDate(toISO(new Date()))
}

async function selectDate(iso: string) {
  selectedDate.value = iso
  await dash.fetchDayLogs(iso)
}

const activeCategory = computed(() =>
  categories.value.find(c => c.id === activeCategoryId.value)
)

const currentDaySlots = computed(() => {
  if (!activeCategory.value) return []
  const day = activeCategory.value.day_schedules.find(d => d.day_of_week === selectedDayKey.value)
  return day?.time_slots ?? []
})

function selectCategory(id: number) { activeCategoryId.value = id }

function getCategoryIcon(type: string): string {
  if (type === 'sport') return '💪'
  if (type === 'daily_tasks') return '✅'
  if (type === 'plans') return '🎯'
  return '📁'
}
function getSlotIcon(t: string): string {
  if (t === 'morning') return '🌅'
  if (t === 'afternoon') return '☀️'
  if (t === 'evening') return '🌆'
  if (t === 'night') return '🌙'
  return '⏰'
}
function getSlotLabel(t: string): string {
  if (t === 'morning') return 'Morning'
  if (t === 'afternoon') return 'Day'
  if (t === 'evening') return 'Evening'
  if (t === 'night') return 'Night'
  return t
}
function getSlotTime(t: string): string {
  if (t === 'morning') return '05:00 – 11:59'
  if (t === 'afternoon') return '12:00 – 17:59'
  if (t === 'evening') return '18:00 – 23:59'
  if (t === 'night') return '00:00 – 04:59'
  return ''
}

function openAddTask(slotId: number) {
  addTaskSlotId.value = slotId
  newTaskTitle.value = ''
  newTaskTime.value = ''
  newTaskRecurring.value = true
}

async function saveTask() {
  if (!newTaskTitle.value.trim() || addTaskSlotId.value === null) return
  await dash.createTask(addTaskSlotId.value, {
    title: newTaskTitle.value.trim(),
    scheduled_time: newTaskTime.value || null,
    is_recurring: newTaskRecurring.value,
  } as Partial<Task>)
  addTaskSlotId.value = null
  // Перезагружаем логи дня — у новой задачи появится pending-лог
  if (selectedDate.value) await dash.fetchDayLogs(selectedDate.value)
}

async function addCategory() {
  if (!newCatTitle.value.trim()) return
  const cat = await dash.createCategory(newCatType.value, newCatTitle.value.trim())
  activeCategoryId.value = cat.id
  showAddCategory.value = false
  newCatTitle.value = ''
}

onMounted(async () => {
  await dash.fetchAll()
  if (dash.categories.length > 0) {
    activeCategoryId.value = dash.categories[0].id
  }
  goToday()
})
</script>

<style scoped>
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
.content { flex: 1; overflow-y: auto; padding: 24px 28px; display: flex; flex-direction: column; gap: 20px; }

.day-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.day-title { font-size: 20px; font-weight: 700; cursor: pointer; }
.day-chevron { font-size: 14px; color: var(--text-2); }
.day-bar-right { display: flex; align-items: center; gap: 8px; }
.day-nav { width: 28px; height: 28px; border-radius: var(--r-md); background: var(--bg); border: 1px solid var(--border); font-size: 16px; color: var(--text-2); display: flex; align-items: center; justify-content: center; }
.day-nav:hover { background: var(--surface-hover); }
.days-row { display: flex; gap: 2px; }
.day-btn { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 6px 10px; border-radius: var(--r-md); min-width: 46px; color: var(--text-2); }
.day-btn:hover { background: var(--surface-hover); color: var(--text); }
.day-btn--active { background: var(--primary); color: white; }
.day-label { font-size: 11px; font-weight: 500; }
.day-num { font-size: 14px; font-weight: 700; }
.today-btn { padding: 6px 14px; background: var(--bg); border: 1px solid var(--border); border-radius: var(--r-md); font-size: 13px; font-weight: 500; }
.today-btn:hover { background: var(--surface-hover); }

.cat-tabs { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.cat-tab { padding: 8px 16px; border-radius: var(--r-xl); font-size: 13.5px; font-weight: 600; background: var(--bg); border: 1.5px solid var(--border); color: var(--text-2); }
.cat-tab:hover { border-color: var(--primary); color: var(--text); }
.cat-tab--active { background: var(--primary); border-color: var(--primary); color: white; }
.cat-tab--add { font-size: 16px; padding: 6px 12px; }

.slots-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.slot-col { background: var(--surface); border-radius: var(--r-lg); border: 1px solid var(--border); padding: 16px; display: flex; flex-direction: column; gap: 12px; min-height: 200px; }
.slot-header { display: flex; align-items: center; gap: 10px; }
.slot-icon { font-size: 20px; }
.slot-title { font-size: 14px; font-weight: 700; }
.slot-time { font-size: 11px; color: var(--text-3); margin-top: 1px; }

.slot-tasks { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.task-item { display: flex; align-items: center; gap: 8px; padding: 6px 4px; border-radius: var(--r-sm); }
.task-item:hover { background: var(--surface-hover); }
.task-check { width: 18px; height: 18px; border-radius: 50%; border: 1.5px solid var(--border); flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.task-check:hover { border-color: var(--primary); }
.task-check--done { background: var(--primary); border-color: var(--primary); color: white; }
.task-title { flex: 1; font-size: 13px; font-weight: 500; }
.task-done { text-decoration: line-through; color: var(--text-3); }
.task-time { font-size: 11px; color: var(--text-3); flex-shrink: 0; }
.task-add { display: flex; align-items: center; gap: 6px; padding: 6px 4px; font-size: 12.5px; color: var(--text-3); border-radius: var(--r-sm); margin-top: 4px; }
.task-add:hover { color: var(--primary); background: var(--primary-light); }

.empty-state { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 80px 0; color: var(--text-2); font-size: 14px; text-align: center; }

.right-panel { width: 260px; min-width: 260px; border-left: 1px solid var(--border); overflow-y: auto; background: var(--surface); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--surface); border-radius: var(--r-xl); padding: 28px; width: 100%; max-width: 360px; box-shadow: var(--shadow-lg); display: flex; flex-direction: column; gap: 16px; }
.modal-title { font-size: 17px; font-weight: 700; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; font-weight: 600; color: var(--text-2); text-transform: uppercase; letter-spacing: 0.04em; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; text-transform: none; cursor: pointer; }
.checkbox-label input { width: 16px; height: 16px; cursor: pointer; }
.input, .select { padding: 9px 12px; border: 1px solid var(--border); border-radius: var(--r-md); font-size: 13.5px; outline: none; background: var(--bg); font-family: inherit; width: 100%; }
.input:focus, .select:focus { border-color: var(--primary); }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px; }
.btn-ghost { padding: 8px 16px; border-radius: var(--r-md); font-size: 13px; font-weight: 600; color: var(--text-2); background: var(--bg); border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--surface-hover); }
.btn-primary-sm { padding: 8px 18px; background: var(--primary); color: white; border-radius: var(--r-md); font-size: 13px; font-weight: 600; border: none; }
.btn-primary-sm:hover { background: var(--primary-hover); }
</style>