const isBrowser = typeof window !== 'undefined'
const fallbackApiBaseUrl = isBrowser && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
  ? 'https://api.herojiatou.com'
  : 'http://127.0.0.1:8010'

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || fallbackApiBaseUrl).replace(/\/$/, '')

export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

export function apiConnectionError(message = '请求后端 API 失败'): Error {
  return new Error(`${message}。当前 API 地址：${API_BASE_URL}。请确认 Vercel 环境变量 NEXT_PUBLIC_API_BASE_URL 指向 https://api.herojiatou.com，且后端服务在线。`)
}

type FetchApiOptions = {
  method?: 'GET' | 'POST'
  timeoutMs?: number
}

export async function fetchApi<T>(path: string, fallback?: T, options: FetchApiOptions = {}): Promise<T> {
  const controller = new AbortController()
  const timeoutId = options.timeoutMs ? setTimeout(() => controller.abort(), options.timeoutMs) : undefined
  try {
    const res = await fetch(apiUrl(path), {
      method: options.method || 'GET',
      signal: controller.signal,
    })
    if (!res.ok) {
      if (fallback !== undefined) return fallback
      throw new Error(`HTTP ${res.status}`)
    }
    return (await res.json()) as T
  } catch (err) {
    if (fallback !== undefined) return fallback
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error(`请求超时。当前 API 地址：${API_BASE_URL}`)
    }
    if (err instanceof Error && err.message.startsWith('HTTP ')) {
      throw err
    }
    throw apiConnectionError()
  } finally {
    if (timeoutId !== undefined) {
      clearTimeout(timeoutId)
    }
  }
}
