import { ref } from 'vue'

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
}

interface PerformanceEntry {
  type: string
  metrics: PerformanceMetric[]
  timestamp: number
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private entries: PerformanceEntry[] = []
  private maxEntries: number = 100
  private isMonitoring: boolean = false
  private metricsBuffer: Map<string, PerformanceMetric[]> = new Map()

  private constructor() {
    this.setupObservers()
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  private setupObservers(): void {
    // 页面加载性能监控
    if (window.PerformanceObserver) {
      // 监控页面加载性能
      const loadObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          if (entry.entryType === 'navigation') {
            this.recordMetric('pageLoad', [
              { name: 'domComplete', value: entry.domComplete, timestamp: Date.now() },
              { name: 'loadEventEnd', value: entry.loadEventEnd, timestamp: Date.now() },
              { name: 'domInteractive', value: entry.domInteractive, timestamp: Date.now() }
            ])
          }
        })
      })
      loadObserver.observe({ entryTypes: ['navigation'] })

      // 监控资源加载性能
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          this.recordMetric('resource', [
            { name: 'duration', value: entry.duration, timestamp: Date.now() },
            { name: 'transferSize', value: (entry as PerformanceResourceTiming).transferSize, timestamp: Date.now() }
          ])
        })
      })
      resourceObserver.observe({ entryTypes: ['resource'] })

      // 监控长任务
      const longTaskObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          this.recordMetric('longTask', [
            { name: 'duration', value: entry.duration, timestamp: Date.now() }
          ])
        })
      })
      longTaskObserver.observe({ entryTypes: ['longtask'] })

      // 监控首次绘制和首次内容绘制
      const paintObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          this.recordMetric('paint', [
            { name: entry.name, value: entry.startTime, timestamp: Date.now() }
          ])
        })
      })
      paintObserver.observe({ entryTypes: ['paint'] })
    }

    // 内存使用监控
    if (window.performance && (performance as any).memory) {
      setInterval(() => {
        const memory = (performance as any).memory
        this.recordMetric('memory', [
          { name: 'usedJSHeapSize', value: memory.usedJSHeapSize, timestamp: Date.now() },
          { name: 'totalJSHeapSize', value: memory.totalJSHeapSize, timestamp: Date.now() }
        ])
      }, 5000)
    }

    // 帧率监控
    let lastTime = performance.now()
    let frames = 0
    const measureFPS = () => {
      frames++
      const currentTime = performance.now()
      if (currentTime >= lastTime + 1000) {
        const fps = Math.round((frames * 1000) / (currentTime - lastTime))
        this.recordMetric('fps', [
          { name: 'fps', value: fps, timestamp: Date.now() }
        ])
        frames = 0
        lastTime = currentTime
      }
      requestAnimationFrame(measureFPS)
    }
    requestAnimationFrame(measureFPS)
  }

  private recordMetric(type: string, metrics: PerformanceMetric[]): void {
    const entry: PerformanceEntry = {
      type,
      metrics,
      timestamp: Date.now()
    }

    this.entries.unshift(entry)
    if (this.entries.length > this.maxEntries) {
      this.entries.pop()
    }

    // 缓存最近的指标
    if (!this.metricsBuffer.has(type)) {
      this.metricsBuffer.set(type, [])
    }
    const buffer = this.metricsBuffer.get(type)!
    buffer.push(...metrics)
    if (buffer.length > this.maxEntries) {
      buffer.splice(0, buffer.length - this.maxEntries)
    }
  }

  public startMonitoring(): void {
    this.isMonitoring = true
  }

  public stopMonitoring(): void {
    this.isMonitoring = false
  }

  public getEntries(): PerformanceEntry[] {
    return this.entries
  }

  public getMetricsByType(type: string): PerformanceMetric[] {
    return this.metricsBuffer.get(type) || []
  }

  public clearEntries(): void {
    this.entries = []
    this.metricsBuffer.clear()
  }

  public getStats(): {
    pageLoadTime: number
    averageResourceLoadTime: number
    longTaskCount: number
    averageFPS: number
    memoryUsage: number
  } {
    const pageLoadMetrics = this.getMetricsByType('pageLoad')
    const resourceMetrics = this.getMetricsByType('resource')
    const longTaskMetrics = this.getMetricsByType('longTask')
    const fpsMetrics = this.getMetricsByType('fps')
    const memoryMetrics = this.getMetricsByType('memory')

    const lastPageLoad = pageLoadMetrics[pageLoadMetrics.length - 1]
    const pageLoadTime = lastPageLoad ? lastPageLoad.value : 0

    const resourceTimes = resourceMetrics.filter(m => m.name === 'duration').map(m => m.value)
    const averageResourceLoadTime = resourceTimes.length > 0
      ? resourceTimes.reduce((a, b) => a + b, 0) / resourceTimes.length
      : 0

    const longTaskCount = longTaskMetrics.length

    const fpsValues = fpsMetrics.map(m => m.value)
    const averageFPS = fpsValues.length > 0
      ? fpsValues.reduce((a, b) => a + b, 0) / fpsValues.length
      : 0

    const lastMemoryUsage = memoryMetrics[memoryMetrics.length - 1]
    const memoryUsage = lastMemoryUsage ? lastMemoryUsage.value : 0

    return {
      pageLoadTime,
      averageResourceLoadTime,
      longTaskCount,
      averageFPS,
      memoryUsage
    }
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance() 