<template>
  <div class="home">
    <h1>自动化测试平台</h1>
    <p>欢迎使用自动化测试平台</p>
    <ErrorTest />
    <NetworkTest />
  </div>
</template>

<script setup lang="ts">
import ErrorTest from '../components/ErrorTest.vue'
import NetworkTest from '../components/NetworkTest.vue'
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

p {
  color: #666;
  font-size: 18px;
}
</style> 