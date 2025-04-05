<template>
  <div class="network-test">
    <h2>网络监控测试</h2>
    
    <div class="actions">
      <button @click="makeSuccessRequest">发送成功请求</button>
      <button @click="makeFailRequest">发送失败请求</button>
      <button @click="clearRequests">清除记录</button>
    </div>

    <div class="stats">
      <h3>统计信息</h3>
      <p>总请求数: {{ stats.totalRequests }}</p>
      <p>成功请求: {{ stats.successfulRequests }}</p>
      <p>失败请求: {{ stats.failedRequests }}</p>
      <p>平均响应时间: {{ Math.round(stats.averageResponseTime) }}ms</p>
    </div>

    <div class="requests">
      <h3>请求记录</h3>
      <div v-for="(request, index) in requests" :key="index" class="request-item">
        <div class="request-header">
          <span :class="['method', request.method.toLowerCase()]">{{ request.method }}</span>
          <span class="url">{{ request.url }}</span>
          <span :class="['status', getStatusClass(request.status)]">
            {{ request.status || '失败' }}
          </span>
          <span class="duration">{{ request.duration }}ms</span>
        </div>
        <div class="request-details" v-if="request.requestData">
          <strong>请求数据:</strong>
          <pre>{{ JSON.stringify(request.requestData, null, 2) }}</pre>
        </div>
        <div class="request-details" v-if="request.responseData">
          <strong>响应数据:</strong>
          <pre>{{ JSON.stringify(request.responseData, null, 2) }}</pre>
        </div>
        <div class="request-details error" v-if="request.error">
          <strong>错误信息:</strong>
          <pre>{{ request.error }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { networkMonitor } from '../utils/networkMonitor'

const requests = ref([])
const stats = ref({
  totalRequests: 0,
  successfulRequests: 0,
  failedRequests: 0,
  averageResponseTime: 0
})

const updateData = () => {
  requests.value = networkMonitor.getRequests()
  stats.value = networkMonitor.getStats()
}

const makeSuccessRequest = async () => {
  try {
    await networkMonitor.getAxiosInstance().get('https://jsonplaceholder.typicode.com/todos/1')
    updateData()
  } catch (error) {
    console.error('请求失败:', error)
  }
}

const makeFailRequest = async () => {
  try {
    await networkMonitor.getAxiosInstance().get('https://jsonplaceholder.typicode.com/invalid-url')
    updateData()
  } catch (error) {
    console.error('请求失败:', error)
    updateData()
  }
}

const clearRequests = () => {
  networkMonitor.clearRequests()
  updateData()
}

const getStatusClass = (status?: number) => {
  if (!status) return 'error'
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400 && status < 500) return 'client-error'
  if (status >= 500) return 'server-error'
  return ''
}

onMounted(() => {
  updateData()
})
</script>

<style scoped>
.network-test {
  padding: 20px;
}

.actions {
  margin-bottom: 20px;
}

button {
  margin-right: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.stats {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.requests {
  margin-top: 20px;
}

.request-item {
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.request-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.method {
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 10px;
  font-weight: bold;
}

.method.get { background-color: #61affe; }
.method.post { background-color: #49cc90; }
.method.put { background-color: #fca130; }
.method.delete { background-color: #f93e3e; }

.url {
  flex-grow: 1;
  margin-right: 10px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 10px;
}

.status.success { background-color: #49cc90; }
.status.client-error { background-color: #fca130; }
.status.server-error { background-color: #f93e3e; }
.status.error { background-color: #f93e3e; }

.duration {
  color: #666;
}

.request-details {
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.request-details.error {
  background-color: #fff5f5;
  color: #f93e3e;
}

pre {
  margin: 5px 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>