<template>
  <div class="dashboard-container">
    <h1>仪表盘</h1>
    <div class="welcome-message">
      欢迎回来，{{ username }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('admin')
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.welcome-message {
  margin-top: 20px;
  font-size: 18px;
  color: #666;
}
</style> 