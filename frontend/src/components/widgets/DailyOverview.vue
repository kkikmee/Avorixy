<template>
  <div class="overview">
    <div class="overview-section">
      <p class="section-title">Daily overview</p>
      <div class="progress-ring-wrap">
        <svg class="ring" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="32" fill="none" stroke="var(--border)" stroke-width="7"/>
          <circle cx="40" cy="40" r="32" fill="none" stroke="var(--primary)" stroke-width="7"
            stroke-dasharray="201" :stroke-dashoffset="201 - (201 * progress / 100)"
            stroke-linecap="round" transform="rotate(-90 40 40)"/>
        </svg>
        <div class="ring-label">
          <span class="ring-pct">{{ progress }}%</span>
          <span class="ring-sub">Progress</span>
        </div>
      </div>
      <p class="progress-hint">+12% from yesterday</p>
    </div>

    <div class="overview-stats">
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        <span class="stat-name">Tasks</span>
        <span class="stat-val">{{ doneCount }} / {{ totalCount }}</span>
      </div>
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        <span class="stat-name">Focus time</span>
        <span class="stat-val">—</span>
      </div>
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <span class="stat-name">Workouts</span>
        <span class="stat-val">—</span>
      </div>
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        <span class="stat-name">Habits</span>
        <span class="stat-val">—</span>
      </div>
    </div>

    <div class="overview-section">
      <p class="section-title">Quick note</p>
      <textarea class="quick-note" placeholder="Write something..." rows="4" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'

const dash = useDashboardStore()

const allTasks = computed(() => {
  const tasks: any[] = []
  for (const cat of dash.categories) {
    for (const day of cat.day_schedules) {
      for (const slot of day.time_slots) {
        tasks.push(...slot.tasks)
      }
    }
  }
  return tasks
})

const totalCount = computed(() => allTasks.value.length)
const doneCount = computed(() => allTasks.value.filter(t => t.status === 'done').length)
const progress = computed(() =>
  totalCount.value === 0 ? 0 : Math.round((doneCount.value / totalCount.value) * 100)
)
</script>

<style scoped>
.overview { padding: 20px 16px; display: flex; flex-direction: column; gap: 20px; }
.section-title { font-size: 13px; font-weight: 700; margin-bottom: 12px; }
.progress-ring-wrap { position: relative; width: 80px; height: 80px; margin: 0 auto 8px; }
.ring { width: 100%; height: 100%; }
.ring-label { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-pct { font-size: 18px; font-weight: 800; }
.ring-sub { font-size: 10px; color: var(--text-2); }
.progress-hint { text-align: center; font-size: 11px; color: var(--green); font-weight: 500; }

.overview-stats { display: flex; flex-direction: column; gap: 8px; }
.stat-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; color: var(--text-2); font-size: 13px; }
.stat-name { flex: 1; }
.stat-val { font-weight: 600; color: var(--text); font-size: 12px; }

.quick-note {
  width: 100%; padding: 10px 12px;
  border: 1px solid var(--border); border-radius: var(--r-md);
  font-size: 13px; resize: none; outline: none;
  background: var(--bg); font-family: inherit; color: var(--text);
  line-height: 1.6;
}
.quick-note:focus { border-color: var(--primary); background: white; }
</style>