<template>
  <router-view></router-view>
  <PerformanceMonitor class="performance-monitor-container" />
</template>

<script setup lang="ts">
import PerformanceMonitor from '@/components/PerformanceMonitor.vue'
// App root component
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.performance-monitor-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
}
</style> 