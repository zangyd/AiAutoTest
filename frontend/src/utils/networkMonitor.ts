import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

interface RequestInfo {
  url: string
  method: string
  requestData?: any
  responseData?: any
  status?: number
  duration: number
  error?: string
  timestamp: number
}

class NetworkMonitor {
  private static instance: NetworkMonitor
  private requests: RequestInfo[] = []
  private maxRequests: number = 100
  private axiosInstance: AxiosInstance

  private constructor() {
    this.axiosInstance = axios.create()
    this.setupInterceptors()
  }

  public static getInstance(): NetworkMonitor {
    if (!NetworkMonitor.instance) {
      NetworkMonitor.instance = new NetworkMonitor()
    }
    return NetworkMonitor.instance
  }

  private setupInterceptors(): void {
    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // 添加请求开始时间
        config.metadata = { startTime: Date.now() }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response) => {
        this.logRequest(response)
        return response
      },
      (error: AxiosError) => {
        this.logError(error)
        return Promise.reject(error)
      }
    )
  }

  private logRequest(response: AxiosResponse): void {
    const config = response.config
    const startTime = (config.metadata as any)?.startTime
    const duration = startTime ? Date.now() - startTime : 0

    const requestInfo: RequestInfo = {
      url: config.url || '',
      method: config.method?.toUpperCase() || 'UNKNOWN',
      requestData: config.data,
      responseData: response.data,
      status: response.status,
      duration,
      timestamp: Date.now()
    }

    this.addRequest(requestInfo)
  }

  private logError(error: AxiosError): void {
    const config = error.config
    const startTime = (config?.metadata as any)?.startTime
    const duration = startTime ? Date.now() - startTime : 0

    const requestInfo: RequestInfo = {
      url: config?.url || '',
      method: config?.method?.toUpperCase() || 'UNKNOWN',
      requestData: config?.data,
      error: error.message,
      duration,
      timestamp: Date.now()
    }

    this.addRequest(requestInfo)
  }

  private addRequest(info: RequestInfo): void {
    this.requests.unshift(info)
    if (this.requests.length > this.maxRequests) {
      this.requests.pop()
    }
  }

  public getRequests(): RequestInfo[] {
    return this.requests
  }

  public clearRequests(): void {
    this.requests = []
  }

  public getAxiosInstance(): AxiosInstance {
    return this.axiosInstance
  }

  public getStats(): {
    totalRequests: number
    successfulRequests: number
    failedRequests: number
    averageResponseTime: number
  } {
    const totalRequests = this.requests.length
    const successfulRequests = this.requests.filter(r => r.status && r.status >= 200 && r.status < 300).length
    const failedRequests = totalRequests - successfulRequests
    const totalDuration = this.requests.reduce((sum, r) => sum + r.duration, 0)
    const averageResponseTime = totalRequests > 0 ? totalDuration / totalRequests : 0

    return {
      totalRequests,
      successfulRequests,
      failedRequests,
      averageResponseTime
    }
  }
}

export const networkMonitor = NetworkMonitor.getInstance()