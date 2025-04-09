<template>
  <div class="not-found-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <div class="error-divider"></div>
      <h2 class="error-title">页面不存在</h2>
      <p class="error-desc">您访问的页面不存在或已被移除</p>
      <router-link to="/" class="back-home">
        返回首页
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404 页面组件
</script>

<style lang="scss" scoped>
@use '../../styles/variables.scss' as *;

.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: $background-color;
}

.error-content {
  text-align: center;
  padding: $spacing-xl;
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  color: $primary-color;
  margin: 0;
  line-height: 1;
  font-weight: 600;
}

.error-divider {
  width: 80px;
  height: 4px;
  background-color: $primary-color;
  margin: $spacing-lg auto;
  border-radius: 2px;
}

.error-title {
  font-size: 32px;
  color: $dark-gray;
  margin: $spacing-lg 0;
}

.error-desc {
  font-size: $font-size-lg;
  color: $gray;
  margin-bottom: $spacing-xl;
}

.back-home {
  display: inline-block;
  padding: $spacing-md $spacing-lg;
  background-color: $primary-color;
  color: $white;
  border-radius: $border-radius-base;
  text-decoration: none;
  font-size: $font-size-base;
  transition: background-color 0.3s;
  
  &:hover {
    background-color: $primary-light;
  }
}
</style> 