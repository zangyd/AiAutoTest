import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Router } from 'vue-router'

export interface UserInfo {
  id: number
  username: string
  email: string
  role: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 路由实例
  const router = ref<Router>()

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      loading.value = true
      // TODO: 调用获取用户信息API
      const response = await fetch('/api/v1/user/info', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      const data = await response.json()
      userInfo.value = data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      loading.value = true
      // TODO: 调用登录API
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })
      const data = await response.json()
      token.value = data.token
      localStorage.setItem('token', data.token)
      await getUserInfo()
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      loading.value = true
      // TODO: 调用登出API
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      token.value = null
      userInfo.value = null
      localStorage.removeItem('token')
      router.value?.push('/login')
    } catch (error) {
      console.error('登出失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    token,
    userInfo,
    loading,
    getUserInfo,
    login,
    logout
  }
}) 