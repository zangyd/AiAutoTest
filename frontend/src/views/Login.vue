<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo-container">
          <img src="../assets/images/logo.png" alt="Logo" class="logo" />
          <h1 class="title">AI自动化测试平台</h1>
        </div>
        <h2 class="subtitle">企业级自动化测试解决方案</h2>
      </div>
      
      <div class="login-form-container">
        <h3 class="form-title">账号登录</h3>
        
        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="form-item">
            <div class="form-label">
              <i class="icon icon-user"></i>
              <label for="username">用户名</label>
            </div>
            <input
              type="text"
              id="username"
              v-model="form.username"
              placeholder="请输入用户名"
              autocomplete="username"
              :class="{ 'error': errors.username }"
              @focus="clearError('username')"
            />
            <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
          </div>
          
          <div class="form-item">
            <div class="form-label">
              <i class="icon icon-lock"></i>
              <label for="password">密码</label>
            </div>
            <div class="password-input">
              <input
                :type="showPassword ? 'text' : 'password'"
                id="password"
                v-model="form.password"
                placeholder="请输入密码"
                autocomplete="current-password"
                :class="{ 'error': errors.password }"
                @focus="clearError('password')"
              />
              <i 
                class="icon" 
                :class="showPassword ? 'icon-eye-open' : 'icon-eye-close'"
                @click="togglePasswordVisibility"
              ></i>
            </div>
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          </div>
          
          <div v-if="isCaptchaEnabled" class="form-item">
            <div class="form-label">
              <i class="icon icon-captcha"></i>
              <label for="captcha">验证码</label>
            </div>
            <div class="captcha-container">
              <input
                type="text"
                id="captcha"
                v-model="form.captcha"
                placeholder="请输入验证码"
                maxlength="6"
                :class="{ 'error': errors.captcha }"
                @focus="clearError('captcha')"
              />
              <div class="captcha-image" @click="refreshCaptcha">
                <img v-if="captchaImageUrl" :src="captchaImageUrl" alt="验证码" />
                <div v-else class="captcha-loading">加载中...</div>
              </div>
            </div>
            <div v-if="errors.captcha" class="error-message">{{ errors.captcha }}</div>
          </div>
          
          <div class="form-options">
            <div class="remember-me">
              <input type="checkbox" id="remember" v-model="form.remember" />
              <label for="remember">记住我</label>
            </div>
            <a href="#" class="forgot-password">忘记密码?</a>
          </div>
          
          <div class="form-submit">
            <button type="submit" :disabled="loading" class="login-button">
              <span v-if="loading">登录中...</span>
              <span v-else>登录</span>
            </button>
          </div>
          
          <div v-if="errorMessage" class="global-error">
            <i class="icon icon-error"></i>
            <span>{{ errorMessage }}</span>
          </div>
        </form>
      </div>
      
      <div class="login-footer">
        <p>Copyright © {{ currentYear }} AI自动化测试平台 All Rights Reserved</p>
      </div>
    </div>
    
    <div class="login-background">
      <div class="bg-decoration"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/modules/user';
import { getCaptcha } from '@/api/user';

// 路由实例
const router = useRouter();
// 用户状态
const userStore = useUserStore();

// 表单数据
const form = reactive({
  username: '',
  password: '',
  captcha: '',
  captcha_id: '',
  remember: false
});

// 错误信息
const errors = reactive({
  username: '',
  password: '',
  captcha: ''
});

// 全局错误信息
const errorMessage = ref('');
// 加载状态
const loading = ref(false);
// 是否显示密码
const showPassword = ref(false);
// 是否启用验证码
const isCaptchaEnabled = ref(true);
// 验证码图片URL
const captchaImageUrl = ref('');

// 当前年份
const currentYear = computed(() => new Date().getFullYear());

// 页面加载时获取验证码
onMounted(async () => {
  if (isCaptchaEnabled.value) {
    await refreshCaptcha();
  }
});

// 刷新验证码
async function refreshCaptcha() {
  try {
    console.log('开始获取验证码...');
    const data = await getCaptcha();
    console.log('验证码获取成功:', data);
    
    // 确保接收到的数据中包含必要的字段
    if (data && data.captcha_id && data.captcha_image) {
      form.captcha_id = data.captcha_id;
      captchaImageUrl.value = data.captcha_image;
      form.captcha = '';
      console.log('验证码ID设置为:', form.captcha_id);
    } else {
      console.error('验证码数据格式异常:', data);
      throw new Error('验证码数据格式异常');
    }
  } catch (error) {
    console.error('获取验证码失败:', error);
    errorMessage.value = '获取验证码失败，请刷新页面重试';
  }
}

// 切换密码可见性
function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

// 清除指定字段的错误信息
function clearError(field: keyof typeof errors) {
  errors[field] = '';
  errorMessage.value = '';
}

// 验证表单
function validateForm() {
  let isValid = true;
  
  // 验证用户名
  if (!form.username.trim()) {
    errors.username = '请输入用户名';
    isValid = false;
  }
  
  // 验证密码
  if (!form.password) {
    errors.password = '请输入密码';
    isValid = false;
  } else if (form.password.length < 6) {
    errors.password = '密码长度不能小于6位';
    isValid = false;
  }
  
  // 验证验证码
  if (isCaptchaEnabled.value && !form.captcha) {
    errors.captcha = '请输入验证码';
    isValid = false;
  }
  
  return isValid;
}

// 提交表单
async function handleSubmit() {
  try {
    if (!validateForm()) {
      return;
    }
    
    loading.value = true;
    errorMessage.value = '';
    
    // 调用登录接口
    const result = await userStore.loginAction(
      form.username,
      form.password,
      form.captcha,
      form.captcha_id
    );
    
    if (result && result.access_token) {
      // 登录成功，跳转到首页
      router.push('/');
    } else {
      // 登录失败，显示错误信息并刷新验证码
      errorMessage.value = '登录失败，请检查用户名和密码';
      await refreshCaptcha();
    }
  } catch (error: any) {
    console.error('登录失败:', error);
    errorMessage.value = error.message || '登录失败，请重试';
    await refreshCaptcha();
  } finally {
    loading.value = false;
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/variables.scss' as *;

.login-page {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: $background-color;
  position: relative;
  overflow: hidden;
}

.login-container {
  display: flex;
  flex-direction: column;
  width: 480px;
  min-height: 600px;
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-base;
  z-index: 2;
  margin: auto;
  padding: $spacing-xl;
  position: relative;
}

.login-header {
  margin-bottom: $spacing-xl;
  text-align: center;
  
  .logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $spacing-md;
    
    .logo {
      width: 40px;
      height: 40px;
      margin-right: $spacing-sm;
    }
    
    .title {
      font-size: 24px;
      font-weight: 600;
      color: $primary-color;
    }
  }
  
  .subtitle {
    font-size: $font-size-lg;
    color: $gray;
    font-weight: 400;
  }
}

.login-form-container {
  flex: 1;
  
  .form-title {
    font-size: 18px;
    font-weight: 500;
    color: $dark-gray;
    margin-bottom: $spacing-lg;
    position: relative;
    padding-left: $spacing-md;
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 16px;
      background-color: $primary-color;
      border-radius: 2px;
    }
  }
}

.login-form {
  .form-item {
    margin-bottom: $spacing-lg;
    
    .form-label {
      display: flex;
      align-items: center;
      margin-bottom: $spacing-xs;
      
      .icon {
        margin-right: $spacing-xs;
        color: $gray;
      }
      
      label {
        font-size: $font-size-base;
        color: $dark-gray;
      }
    }
    
    input {
      width: 100%;
      height: 40px;
      padding: $spacing-sm $spacing-md;
      border: $border-width solid $border-color;
      border-radius: $border-radius-base;
      font-size: $font-size-base;
      color: $dark-gray;
      transition: all 0.3s;
      
      &:focus {
        border-color: $primary-light;
        box-shadow: 0 0 0 2px rgba($primary-color, 0.2);
        outline: none;
      }
      
      &.error {
        border-color: $error-color;
      }
      
      &::placeholder {
        color: $light-gray;
      }
    }
    
    .error-message {
      color: $error-color;
      font-size: $font-size-sm;
      margin-top: $spacing-xs;
    }
    
    .password-input {
      position: relative;
      
      .icon {
        position: absolute;
        right: $spacing-md;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: $light-gray;
        
        &:hover {
          color: $gray;
        }
      }
    }
    
    .captcha-container {
      display: flex;
      
      input {
        flex: 1;
        margin-right: $spacing-md;
      }
      
      .captcha-image {
        width: 120px;
        height: 40px;
        border: $border-width solid $border-color;
        border-radius: $border-radius-base;
        overflow: hidden;
        cursor: pointer;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .captcha-loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: $light-gray;
          font-size: $font-size-sm;
        }
      }
    }
  }
  
  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-lg;
    
    .remember-me {
      display: flex;
      align-items: center;
      
      input[type="checkbox"] {
        margin-right: $spacing-xs;
      }
      
      label {
        color: $gray;
        font-size: $font-size-base;
      }
    }
    
    .forgot-password {
      color: $primary-color;
      font-size: $font-size-base;
      
      &:hover {
        color: $primary-light;
      }
    }
  }
  
  .form-submit {
    margin-bottom: $spacing-lg;
    
    .login-button {
      width: 100%;
      height: 40px;
      background-color: $primary-color;
      color: $white;
      font-size: $font-size-base;
      border: none;
      border-radius: $border-radius-base;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background-color: $primary-light;
      }
      
      &:disabled {
        background-color: $light-gray;
        cursor: not-allowed;
      }
    }
  }
  
  .global-error {
    display: flex;
    align-items: center;
    justify-content: center;
    color: $error-color;
    font-size: $font-size-base;
    
    .icon {
      margin-right: $spacing-xs;
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: $spacing-xl;
  
  p {
    color: $light-gray;
    font-size: $font-size-sm;
  }
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  
  .bg-decoration {
    position: absolute;
    width: 200%;
    height: 200%;
    top: -50%;
    left: -50%;
    background: radial-gradient(ellipse at center, rgba($primary-light, 0.1) 0%, rgba($primary-color, 0.05) 70%, rgba($primary-dark, 0.02) 100%);
    transform: rotate(30deg);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: -10%;
    right: -10%;
    width: 60%;
    height: 60%;
    background: radial-gradient(circle, rgba($primary-light, 0.2) 0%, rgba($primary-color, 0.1) 50%, transparent 70%);
    border-radius: 50%;
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: -10%;
    left: -10%;
    width: 70%;
    height: 70%;
    background: radial-gradient(circle, rgba($primary-dark, 0.2) 0%, rgba($primary-color, 0.1) 50%, transparent 70%);
    border-radius: 50%;
  }
}

// 响应式调整
@media (max-width: 768px) {
  .login-container {
    width: 100%;
    height: 100%;
    border-radius: 0;
    margin: 0;
    padding: $spacing-lg;
  }
}

// 图标样式（使用伪元素模拟）
.icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  position: relative;
  
  &.icon-user::before {
    content: '👤';
  }
  
  &.icon-lock::before {
    content: '🔒';
  }
  
  &.icon-captcha::before {
    content: '🖼️';
  }
  
  &.icon-eye-open::before {
    content: '👁️';
  }
  
  &.icon-eye-close::before {
    content: '👁️‍🗨️';
  }
  
  &.icon-error::before {
    content: '❌';
  }
}
</style> 