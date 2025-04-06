<template>
  <div class="login-container">
    <h1>登录 - 自动化测试平台</h1>
    <form @submit.prevent="handleSubmit" class="login-form">
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          name="username" 
          v-model="form.username" 
          required
          placeholder="请输入用户名"
        />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          name="password" 
          v-model="form.password" 
          required
          placeholder="请输入密码"
        />
      </div>
      <div class="form-group">
        <button type="submit">登录</button>
      </div>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const error = ref('')
const form = reactive({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  try {
    // TODO: 实现登录逻辑
    if (form.username === 'admin' && form.password === 'admin') {
      await router.push('/dashboard')
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (e) {
    error.value = '登录失败，请稍后重试'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
}

.login-form {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #40a9ff;
}

.error-message {
  color: #ff4d4f;
  text-align: center;
  margin-top: 16px;
}
</style> 