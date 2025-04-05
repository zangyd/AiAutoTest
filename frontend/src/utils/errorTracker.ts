import { App } from 'vue'

interface ErrorInfo {
  error: Error
  info: string
  url: string
  time: string
  userAgent: string
  componentName?: string
}

class ErrorTracker {
  private static instance: ErrorTracker
  private app: App | null = null
  private errorList: ErrorInfo[] = []
  private readonly maxErrors: number = 100
  private readonly reportUrl: string = '/api/error/report'

  private constructor() {
    this.setupWindowErrorHandler()
    this.setupPromiseErrorHandler()
  }

  public static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker()
    }
    return ErrorTracker.instance
  }

  public init(app: App): void {
    this.app = app
    this.setupVueErrorHandler()
  }

  private setupWindowErrorHandler(): void {
    window.onerror = (message, source, lineno, colno, error) => {
      this.handleError({
        error: error || new Error(String(message)),
        info: `${message} at ${source}:${lineno}:${colno}`,
        url: window.location.href,
        time: new Date().toISOString(),
        userAgent: navigator.userAgent
      })
    }
  }

  private setupPromiseErrorHandler(): void {
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        error: event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
        info: 'Unhandled Promise Rejection',
        url: window.location.href,
        time: new Date().toISOString(),
        userAgent: navigator.userAgent
      })
    })
  }

  private setupVueErrorHandler(): void {
    if (!this.app) return

    this.app.config.errorHandler = (error, instance, info) => {
      this.handleError({
        error: error instanceof Error ? error : new Error(String(error)),
        info: info,
        url: window.location.href,
        time: new Date().toISOString(),
        userAgent: navigator.userAgent,
        componentName: instance?.$options.name
      })
    }
  }

  private handleError(errorInfo: ErrorInfo): void {
    console.error('Error tracked:', errorInfo)
    this.errorList.push(errorInfo)
    
    // 保持错误列表在最大限制以内
    if (this.errorList.length > this.maxErrors) {
      this.errorList.shift()
    }

    // 上报错误
    this.reportError(errorInfo)
  }

  private async reportError(errorInfo: ErrorInfo): Promise<void> {
    try {
      if (process.env.NODE_ENV === 'production') {
        const response = await fetch(this.reportUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(errorInfo)
        })
        
        if (!response.ok) {
          console.error('Error reporting failed:', response.statusText)
        }
      }
    } catch (error) {
      console.error('Error while reporting error:', error)
    }
  }

  public getErrors(): ErrorInfo[] {
    return [...this.errorList]
  }

  public clearErrors(): void {
    this.errorList = []
  }
}

export default ErrorTracker.getInstance() 