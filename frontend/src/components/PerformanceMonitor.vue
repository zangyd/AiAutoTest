<template>
  <div class="performance-monitor">
    <h3>性能监控</h3>
    <div class="metrics-grid">
      <div class="metric-card" v-for="(value, key) in formattedStats" :key="key">
        <div class="metric-name">{{ metricLabels[key] }}</div>
        <div class="metric-value">{{ value }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, computed } from 'vue'
import { performanceMonitor } from '@/utils/performanceMonitor'

export default defineComponent({
  name: 'PerformanceMonitor',
  setup() {
    const stats = ref({
      pageLoadTime: 0,
      averageResourceLoadTime: 0,
      longTaskCount: 0,
      averageFPS: 0,
      memoryUsage: 0
    })

    const metricLabels = {
      pageLoadTime: '页面加载时间',
      averageResourceLoadTime: '平均资源加载时间',
      longTaskCount: '长任务数量',
      averageFPS: '平均帧率',
      memoryUsage: '内存使用'
    }

    const updateStats = () => {
      stats.value = performanceMonitor.getStats()
    }

    const formatValue = (key: string, value: number): string => {
      switch (key) {
        case 'pageLoadTime':
        case 'averageResourceLoadTime':
          return `${value.toFixed(2)}ms`
        case 'averageFPS':
          return `${value.toFixed(1)} FPS`
        case 'memoryUsage':
          return `${(value / (1024 * 1024)).toFixed(2)}MB`
        default:
          return value.toString()
      }
    }

    const formattedStats = computed(() => {
      const result: Record<string, string> = {}
      for (const [key, value] of Object.entries(stats.value)) {
        result[key] = formatValue(key, value)
      }
      return result
    })

    let intervalId: number

    onMounted(() => {
      performanceMonitor.startMonitoring()
      updateStats()
      intervalId = window.setInterval(updateStats, 1000)
    })

    onUnmounted(() => {
      performanceMonitor.stopMonitoring()
      window.clearInterval(intervalId)
    })

    return {
      stats,
      metricLabels,
      formattedStats
    }
  }
})
</script>

<style scoped>
.performance-monitor {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.metric-card {
  background-color: white;
  padding: 1rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-name {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #212529;
}
</style> 