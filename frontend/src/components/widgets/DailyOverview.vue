<template>
  <div class="overview">
    <div class="overview-section">
      <p class="section-title">Daily overview</p>
      <div class="progress-ring-wrap">
        <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="32" fill="none" stroke="#E8EAED" stroke-width="7"/>
          <circle cx="40" cy="40" r="32" fill="none" stroke="#6C47FF" stroke-width="7"
            stroke-dasharray="201" :stroke-dashoffset="201 - (201 * progress / 100)"
            stroke-linecap="round" transform="rotate(-90 40 40)"/>
        </svg>
        <div class="ring-label">
          <span class="ring-pct">{{ progress }}%</span>
          <span class="ring-sub">Progress</span>
        </div>
      </div>
    </div>

    <div class="overview-stats">
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        <span class="stat-name">Tasks</span>
        <span class="stat-val">{{ doneCount }} / {{ totalCount }}</span>
      </div>
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        <span class="stat-name">Skipped</span>
        <span class="stat-val">{{ skippedCount }}</span>
      </div>
      <div class="stat-row">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v4l2.5 2.5"/></svg>
        <span class="stat-name">Pending</span>
        <span class="stat-val">{{ pendingCount }}</span>
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

const totalCount = computed(() => dash.dayStats?.total ?? 0)
const doneCount = computed(() => dash.dayStats?.done ?? 0)
const skippedCount = computed(() => dash.dayStats?.skipped ?? 0)
const pendingCount = computed(() => dash.dayStats?.pending ?? 0)
const progress = computed(() => dash.dayStats?.progress_pct ?? 0)
</script>

<style scoped>
.overview { padding: 20px 16px; display: flex; flex-direction: column; gap: 20px; }
.section-title { font-size: 13px; font-weight: 700; margin-bottom: 12px; }

.progress-ring-wrap {
  position: relative;
  width: 90px;
  height: 90px;
  margin: 0 auto 8px;
  background: transparent;
}
.progress-ring-wrap svg {
  width: 90px;
  height: 90px;
  display: block;
  overflow: visible;
  background: transparent;
}
.ring-label {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-pct { font-size: 18px; font-weight: 800; color: var(--text); }
.ring-sub { font-size: 10px; color: var(--text-2); }

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
.quick-note:focus { border-color: var(--primary); }
</style>