<template>
  <div class="error-test">
    <h2>错误追踪测试</h2>
    <div class="buttons">
      <button @click="triggerSyncError">触发同步错误</button>
      <button @click="triggerAsyncError">触发异步错误</button>
      <button @click="triggerPromiseError">触发Promise错误</button>
    </div>
    <div v-if="errors.length > 0" class="error-list">
      <h3>捕获的错误:</h3>
      <ul>
        <li v-for="(error, index) in errors" :key="index">
          {{ error.time }} - {{ error.info }}
        </li>
      </ul>
      <button @click="clearErrors">清除错误列表</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import errorTracker from '../utils/errorTracker'

const errors = ref(errorTracker.getErrors())

// 同步错误
const triggerSyncError = () => {
  throw new Error('这是一个同步错误')
}

// 异步错误
const triggerAsyncError = async () => {
  setTimeout(() => {
    throw new Error('这是一个异步错误')
  }, 100)
}

// Promise错误
const triggerPromiseError = () => {
  Promise.reject(new Error('这是一个Promise错误'))
}

// 清除错误列表
const clearErrors = () => {
  errorTracker.clearErrors()
  errors.value = []
}

// 定期更新错误列表
onMounted(() => {
  setInterval(() => {
    errors.value = errorTracker.getErrors()
  }, 1000)
})
</script>

<style scoped>
.error-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  justify-content: center;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.error-list {
  margin-top: 20px;
  text-align: left;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
}

.error-list ul {
  list-style-type: none;
  padding: 0;
}

.error-list li {
  margin: 10px 0;
  padding: 10px;
  background-color: #fff;
  border-left: 4px solid #ff4444;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style> 