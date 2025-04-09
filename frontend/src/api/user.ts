import request from './request';

// 登录参数接口
interface LoginParams {
  username: string;
  password: string;
  captcha_text?: string;
  captcha_id?: string;
  remember?: boolean;
}

// 登录响应接口
interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 获取验证码接口
interface CaptchaResponse {
  captcha_id: string;
  captcha_image: string;
  expire_in: number;
}

// 用户信息接口
interface UserInfo {
  id: number;
  username: string;
  name: string;
  avatar?: string;
  email: string;
  role: string;
  permissions: string[];
}

/**
 * 用户登录
 * @param params 登录参数
 * @returns 返回登录结果，包含访问令牌和刷新令牌
 */
export function login(params: LoginParams) {
  console.group('登录请求');
  console.log('发送登录请求，参数:', { 
    username: params.username,
    password: '******',
    captcha_text: params.captcha_text ? '******' : undefined,
    captcha_id: params.captcha_id
  });
  
  // 使用URLSearchParams方式发送，适配FastAPI的Form参数
  const formData = new URLSearchParams();
  formData.append('username', params.username);
  formData.append('password', params.password);
  
  // 如果有验证码参数，添加到请求中
  if (params.captcha_text && params.captcha_id) {
    console.log('添加验证码参数:', { 
      captcha_id: params.captcha_id,
      captcha_text_length: params.captcha_text.length
    });
    formData.append('captcha_text', params.captcha_text);
    formData.append('captcha_id', params.captcha_id);
  } else {
    console.log('未提供验证码参数');
  }
  
  console.log('发送的表单数据:', formData.toString().replace(/password=[^&]+/, 'password=******'));
  
  return fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData
  })
  .then(async response => {
    console.log('收到响应:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    });
    
    const responseText = await response.text();
    console.log('响应内容:', responseText);
    
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('解析响应JSON失败:', parseError);
      throw new Error('服务器响应格式错误');
    }
    
    if (!response.ok) {
      console.error('登录失败:', {
        status: response.status,
        data: data
      });
      
      // 处理特定的错误情况
      if (response.status === 400) {
        console.warn('验证码验证失败');
        throw new Error(data.detail || '验证码验证失败');
      } else if (response.status === 401) {
        console.warn('用户名或密码错误');
        throw new Error(data.detail || '用户名或密码错误');
      } else {
        throw new Error(data.detail || '登录失败，请重试');
      }
    }
    
    // 验证响应数据格式
    if (!data.access_token || !data.refresh_token) {
      console.error('响应格式错误:', data);
      throw new Error('登录响应格式错误');
    }
    
    console.log('登录成功，响应数据:', {
      ...data,
      access_token: '******',
      refresh_token: '******'
    });
    console.groupEnd();
    return data;
  })
  .catch(error => {
    console.error('登录请求失败:', error);
    console.groupEnd();
    throw error;
  });
}

/**
 * 获取验证码
 * @returns 返回验证码ID和图片
 */
export function getCaptcha() {
  console.group('获取验证码');
  console.log('发送验证码请求');
  
  return fetch('/api/v1/auth/captcha', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('验证码响应状态:', response.status);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('验证码获取成功:', {
      captcha_id: data.captcha_id,
      expire_in: data.expire_in
    });
    console.groupEnd();
    return data;
  })
  .catch(error => {
    console.error('获取验证码失败:', error);
    console.groupEnd();
    throw error;
  });
}

/**
 * 获取当前用户信息
 * @returns 返回用户详细信息
 */
export function getUserInfo() {
  return request.get<any, LoginResponse['user']>('/api/v1/auth/user-info');
}

/**
 * 用户登出
 * @returns 返回退出结果
 */
export function logout() {
  return request.post('/api/v1/auth/logout');
}

/**
 * 刷新token
 * @returns 返回新的token
 */
export function refreshToken() {
  return request.post<any, { token: string }>('/api/v1/auth/refresh-token');
} 