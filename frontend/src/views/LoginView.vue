<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <span class="logo-icon">A</span>
        <span class="logo-text">Avorixy</span>
      </div>
      <h1 class="auth-title">Добро пожаловать</h1>
      <p class="auth-sub">Войди в свой аккаунт</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="field">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required />
        </div>
        <p v-if="error" class="auth-error">{{ error }}</p>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Входим...' : 'Войти' }}
        </button>
      </form>

      <p class="auth-footer">
        Нет аккаунта?
        <router-link to="/register">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}
.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--surface);
  border-radius: var(--r-xl);
  padding: 40px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
}
.auth-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 28px;
}
.logo-icon {
  width: 32px; height: 32px;
  background: var(--primary);
  color: white;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px;
}
.logo-text { font-weight: 700; font-size: 18px; }
.auth-title { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.auth-sub { color: var(--text-2); font-size: 14px; margin-bottom: 28px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 13px; font-weight: 500; color: var(--text-2); }
.field input {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-size: 14px;
  outline: none;
  background: var(--bg);
  transition: border-color 0.15s;
}
.field input:focus { border-color: var(--primary); background: white; }
.auth-error { font-size: 13px; color: var(--red); }
.btn-primary {
  padding: 11px;
  background: var(--primary);
  color: white;
  border-radius: var(--r-md);
  font-size: 14px;
  font-weight: 600;
  margin-top: 4px;
}
.btn-primary:hover:not(:disabled) { background: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.auth-footer { margin-top: 20px; text-align: center; font-size: 13px; color: var(--text-2); }
.auth-footer a { color: var(--primary); font-weight: 500; }
</style>