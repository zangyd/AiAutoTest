<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <h1>AI自动化测试平台</h1>
    </header>
    
    <div class="dashboard-content">
      <div class="welcome-card">
        <h2>欢迎回来，{{ username }}</h2>
        <p>今天是 {{ currentDate }}</p>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <h3>测试项目</h3>
          <div class="stat-value">12</div>
        </div>
        <div class="stat-card">
          <h3>测试用例</h3>
          <div class="stat-value">342</div>
        </div>
        <div class="stat-card">
          <h3>本周执行</h3>
          <div class="stat-value">86</div>
        </div>
        <div class="stat-card">
          <h3>通过率</h3>
          <div class="stat-value">98.3%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const username = ref('管理员')

// 获取当前日期并格式化
const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  })
})
</script>

<style lang="scss" scoped>
@use '../styles/variables.scss' as *;

.dashboard-container {
  min-height: 100vh;
  background-color: $background-color;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  background-color: $primary-color;
  color: $white;
  padding: $spacing-lg $spacing-xl;
  box-shadow: $box-shadow-base;
  
  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
  }
}

.dashboard-content {
  flex: 1;
  padding: $spacing-xl;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.welcome-card {
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-xl;
  margin-bottom: $spacing-xl;
  box-shadow: $box-shadow-light;
  
  h2 {
    margin: 0 0 $spacing-md 0;
    color: $dark-gray;
    font-weight: 500;
  }
  
  p {
    margin: 0;
    color: $gray;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: $spacing-lg;
}

.stat-card {
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  text-align: center;
  box-shadow: $box-shadow-light;
  transition: transform 0.3s, box-shadow 0.3s;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: $box-shadow-base;
  }
  
  h3 {
    margin: 0 0 $spacing-md 0;
    color: $gray;
    font-weight: 500;
    font-size: $font-size-base;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: $primary-color;
  }
}

// 响应式调整
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style> 