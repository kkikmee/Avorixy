<template>
  <header class="header">
    <div class="header-left">
      <div class="greeting">
        <h1 class="greeting-title">Good morning, {{ auth.user?.username }} 👋</h1>
        <p class="greeting-sub">Here's what's happening with your day.</p>
      </div>
    </div>
    <div class="header-right">
      <div class="search-box">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input placeholder="Search anything..." />
        <span class="kbd">⌘K</span>
      </div>
      <button class="icon-btn">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>
      </button>
      <div class="avatar">{{ userInitial }}</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const userInitial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'U')
</script>

<style scoped>
.header {
  height: var(--header-height);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 10;
}
.greeting-title { font-size: 17px; font-weight: 700; }
.greeting-sub { font-size: 12.5px; color: var(--text-2); margin-top: 1px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.search-box {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 7px 12px;
  color: var(--text-2); min-width: 220px;
}
.search-box input {
  border: none; background: none; outline: none;
  font-size: 13px; color: var(--text); flex: 1;
}
.search-box input::placeholder { color: var(--text-3); }
.kbd {
  font-size: 11px; color: var(--text-3);
  background: var(--border-light); border-radius: 4px;
  padding: 2px 5px; font-family: monospace;
}
.icon-btn {
  width: 34px; height: 34px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-2); background: var(--bg); border: 1px solid var(--border);
}
.icon-btn:hover { background: var(--surface-hover); color: var(--text); }
.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--primary); color: white;
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}
</style>