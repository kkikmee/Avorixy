import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)
      const { data } = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, username: string, password: string) {
    loading.value = true
    try {
      await api.post('/auth/register', { email, username, password })
      await login(email, password)
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me')
    user.value = data
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  async function init() {
    if (localStorage.getItem('access_token')) {
      try {
        await fetchMe()
      } catch {
        logout()
      }
    }
  }

  return { user, loading, isAuthenticated, login, register, logout, init, fetchMe }
})