import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Router } from 'vue-router'
import { login, getUserInfo, logout, refreshToken } from '@/api/user'

export interface UserInfo {
  id: number
  username: string
  email: string
  role: string
  avatar?: string
}

interface UserState {
  token: string
  refreshToken: string
  userId: number | null
  username: string
  name: string
  avatar: string
  email: string
  role: string
  permissions: string[]
  isLoggedIn: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
    userId: null,
    username: '',
    name: '',
    avatar: '',
    email: '',
    role: '',
    permissions: [],
    isLoggedIn: !!localStorage.getItem('token')
  }),
  
  getters: {
    // 获取用户权限
    userPermissions: (state) => state.permissions,
    
    // 判断用户是否有特定权限
    hasPermission: (state) => (permission: string) => {
      return state.permissions.includes(permission)
    }
  },
  
  actions: {
    // 设置token
    setToken(token: string, refreshToken: string) {
      this.token = token
      this.refreshToken = refreshToken
      localStorage.setItem('token', token)
      localStorage.setItem('refreshToken', refreshToken)
      this.isLoggedIn = true
    },
    
    // 清除token
    clearToken() {
      this.token = ''
      this.refreshToken = ''
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      this.isLoggedIn = false
    },
    
    // 设置用户信息
    setUserInfo(userInfo: Partial<UserState>) {
      this.userId = userInfo.userId || this.userId
      this.username = userInfo.username || this.username
      this.name = userInfo.name || this.name
      this.avatar = userInfo.avatar || this.avatar
      this.email = userInfo.email || this.email
      this.role = userInfo.role || this.role
      this.permissions = userInfo.permissions || this.permissions
    },
    
    // 清除用户信息
    clearUserInfo() {
      this.userId = null
      this.username = ''
      this.name = ''
      this.avatar = ''
      this.email = ''
      this.role = ''
      this.permissions = []
    },
    
    // 登录方法
    async loginAction(username: string, password: string, captcha?: string, captchaId?: string) {
      try {
        console.log('登录参数:', {
          username,
          password: '******', // 不输出实际密码 
          captcha_text: captcha,
          captcha_id: captchaId
        });
        
        const response = await login({
          username,
          password,
          captcha_text: captcha,
          captcha_id: captchaId
        })
        
        console.log('登录响应:', response);
        
        // 验证响应中是否包含必要的字段
        if (!response || !response.access_token || !response.refresh_token) {
          throw new Error('登录响应格式错误，缺少token');
        }
        
        // 存储token
        this.setToken(response.access_token, response.refresh_token)
        
        // 获取用户信息
        await this.getUserInfoAction()
        
        return response
      } catch (error: any) {
        console.error('登录失败详细信息:', error);
        this.clearToken()
        this.clearUserInfo()
        
        // 提取更有意义的错误信息
        let errorMsg = '登录失败，请稍后重试';
        if (error.message) {
          errorMsg = error.message;
        }
        
        throw new Error(errorMsg);
      }
    },
    
    // 获取用户信息
    async getUserInfoAction() {
      try {
        if (!this.token) {
          throw new Error('Token不存在')
        }
        
        const userInfo = await getUserInfo()
        
        this.setUserInfo({
          userId: userInfo.id,
          username: userInfo.username,
          name: userInfo.name,
          avatar: userInfo.avatar || '',
          email: userInfo.email,
          role: userInfo.role,
          permissions: userInfo.permissions
        })
        
        return userInfo
      } catch (error) {
        this.clearToken()
        this.clearUserInfo()
        throw error
      }
    },
    
    // 登出方法
    async logoutAction() {
      try {
        if (this.token) {
          await logout()
        }
      } catch (error) {
        console.error('登出失败', error)
      } finally {
        this.clearToken()
        this.clearUserInfo()
      }
    },
    
    // 刷新token
    async refreshTokenAction() {
      try {
        const response = await refreshToken()
        if (!response || !response.access_token) {
          throw new Error('刷新token失败，响应格式错误')
        }
        this.setToken(response.access_token, response.refresh_token || this.refreshToken)
        return response.access_token
      } catch (error) {
        this.clearToken()
        this.clearUserInfo()
        throw error
      }
    }
  }
}) 