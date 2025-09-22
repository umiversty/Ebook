import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Polyfill matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Polyfill postMessage if needed
if (!window.postMessage) {
  window.postMessage = vi.fn()
}

// Add any other missing browser APIs here

const resizeObserverCallbacks: ResizeObserverCallback[] = []

class TestResizeObserver implements ResizeObserver {
  public observe = vi.fn()
  public unobserve = vi.fn()
  public disconnect = vi.fn()
  public takeRecords = vi.fn().mockReturnValue<ResizeObserverEntry[]>([])

  constructor(private readonly callback: ResizeObserverCallback) {
    resizeObserverCallbacks.push(callback)
  }
}

Object.defineProperty(globalThis, '__resizeObserverCallbacks__', {
  configurable: true,
  writable: false,
  value: resizeObserverCallbacks
})

Object.defineProperty(globalThis, 'ResizeObserver', {
  configurable: true,
  writable: true,
  value: TestResizeObserver
})
