<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <span class="logo-icon">A</span>
      <span class="logo-name">Avorixy</span>
    </div>

    <!-- Main nav -->
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="nav-item--active">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        Dashboard
      </router-link>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        Tasks
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
        Plans
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
        Calendar
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        Habits
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Notes
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        Goals
      </a>
      <a class="nav-item">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        Analytics
      </a>
    </nav>

    <!-- Categories -->
    <div class="sidebar-section">
      <p class="section-label">Categories</p>
      <div v-if="loading" class="cat-loading">Загрузка...</div>
      <div v-else>
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="cat-item"
          :class="{ 'cat-item--active': activeCategoryId === cat.id }"
          @click="$emit('select-category', cat.id)"
        >
          <span class="cat-icon">{{ categoryIcon(cat.type) }}</span>
          <span class="cat-name">{{ cat.title }}</span>
          <span v-if="activeCategoryId === cat.id" class="cat-dot" />
        </button>

        <button class="cat-add" @click="$emit('add-category')">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Add category
        </button>
      </div>
    </div>

    <!-- Bottom -->
    <div class="sidebar-bottom">
      <div class="upgrade-card">
        <p class="upgrade-text">Focus better.<br>Achieve more.<br>Start simple.</p>
        <button class="upgrade-btn">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          Upgrade to Pro
        </button>
      </div>

      <div class="sidebar-user" @click="auth.logout()">
        <div class="user-avatar">{{ userInitial }}</div>
        <span class="user-name">{{ auth.user?.username }}</span>
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import type { CategoryType } from '@/types'

defineProps<{ activeCategoryId: number | null }>()
defineEmits(['select-category', 'add-category'])

const auth = useAuthStore()
const dash = useDashboardStore()
const categories = computed(() => dash.categories)
const loading = computed(() => dash.loading)
const userInitial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'U')

function categoryIcon(type: CategoryType) {
  return { sport: '💪', daily_tasks: '✅', plans: '🎯' }[type] ?? '📁'
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  overflow-y: auto;
  position: sticky;
  top: 0;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 8px 16px;
}
.logo-icon {
  width: 28px; height: 28px;
  background: var(--primary); color: white;
  border-radius: 7px; display: flex; align-items: center;
  justify-content: center; font-weight: 800; font-size: 14px;
}
.logo-name { font-weight: 700; font-size: 16px; }

.sidebar-nav { display: flex; flex-direction: column; gap: 1px; }
.nav-item {
  display: flex; align-items: center; gap: 9px;
  padding: 8px 10px; border-radius: var(--r-md);
  font-size: 13.5px; font-weight: 500; color: var(--text-2);
  cursor: pointer;
}
.nav-item:hover { background: var(--surface-hover); color: var(--text); }
.nav-item--active { background: var(--primary-light); color: var(--primary); }

.sidebar-section { margin-top: 20px; flex: 1; }
.section-label { font-size: 11px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.06em; padding: 0 10px; margin-bottom: 6px; }
.cat-loading { font-size: 12px; color: var(--text-3); padding: 8px 10px; }

.cat-item {
  width: 100%; display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; border-radius: var(--r-md);
  font-size: 13px; font-weight: 500; color: var(--text-2); cursor: pointer;
}
.cat-item:hover { background: var(--surface-hover); color: var(--text); }
.cat-item--active { color: var(--text); }
.cat-icon { font-size: 14px; }
.cat-name { flex: 1; text-align: left; }
.cat-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--primary); }

.cat-add {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 10px; width: 100%;
  font-size: 13px; color: var(--text-3); cursor: pointer;
  border-radius: var(--r-md);
}
.cat-add:hover { background: var(--surface-hover); color: var(--text-2); }

.sidebar-bottom { margin-top: auto; padding-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.upgrade-card {
  background: var(--primary-light);
  border-radius: var(--r-lg); padding: 14px;
}
.upgrade-text { font-size: 12px; color: var(--text-2); line-height: 1.6; margin-bottom: 10px; }
.upgrade-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 12px; background: var(--primary);
  color: white; border-radius: var(--r-md);
  font-size: 12px; font-weight: 600; cursor: pointer;
}
.upgrade-btn:hover { background: var(--primary-hover); }

.sidebar-user {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border-radius: var(--r-md); cursor: pointer;
}
.sidebar-user:hover { background: var(--surface-hover); }
.user-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--primary); color: white;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.user-name { flex: 1; font-size: 13px; font-weight: 500; }
</style>