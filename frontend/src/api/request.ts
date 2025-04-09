import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', // 设置API基础URL
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    
    // 如果存在token，则添加到请求头中
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    console.error('请求错误', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 检查响应直接是否就是数据（FastAPI可能直接返回数据而不是包装格式）
    if (!response.data.hasOwnProperty('code')) {
      return response.data;
    }
    
    const { code, data, message } = response.data;
    
    // 如果接口返回成功
    if (code === 200) {
      return data;
    }
    
    // 处理特定错误码
    switch (code) {
      case 401: // 未授权
        // 清除token并跳转到登录页
        localStorage.removeItem('token');
        window.location.href = '/login';
        break;
      case 403: // 权限不足
        console.error('权限不足');
        break;
      default:
        console.error(message || '请求失败');
    }
    
    return Promise.reject(new Error(message || '请求失败'));
  },
  (error: AxiosError) => {
    console.error('请求错误详情:', error);
    if (error.response) {
      const { status } = error.response;
      
      // 提取错误信息
      let errorMessage = '未知错误';
      try {
        const data = error.response.data as any;
        // 尝试获取FastAPI的错误信息
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map((item: any) => item.msg || item).join(', ');
          }
        } else if (data.message) {
          errorMessage = data.message;
        }
      } catch (e) {
        console.error('解析错误信息失败', e);
      }
      
      // 处理HTTP状态码
      switch (status) {
        case 401:
          localStorage.removeItem('token');
          window.location.href = '/login';
          errorMessage = '未授权，请重新登录';
          break;
        case 403:
          errorMessage = '权限不足';
          console.error(errorMessage);
          break;
        case 404:
          errorMessage = '请求资源不存在';
          console.error(errorMessage);
          break;
        case 422:
          errorMessage = '请求参数验证失败: ' + errorMessage;
          console.error(errorMessage);
          break;
        case 500:
          errorMessage = '服务器错误';
          console.error(errorMessage);
          break;
        default:
          console.error(errorMessage);
      }
      
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      console.error('网络错误，请检查网络连接');
      return Promise.reject(new Error('网络错误，请检查网络连接'));
    } else {
      console.error('请求配置错误');
      return Promise.reject(new Error('请求配置错误'));
    }
  }
);

export default request; 