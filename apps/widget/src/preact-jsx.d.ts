// Type declarations for Preact JSX runtime
// This file provides JSX types when using jsx: "react-jsx" with jsxImportSource: "preact"

declare module 'preact/jsx-runtime' {
  export namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any
    }
  }
  
  export function jsx(type: any, props: any, key?: any): any
  export function jsxs(type: any, props: any, key?: any): any
  export function Fragment(props: { children?: any }): any
}

declare module 'preact/hooks' {
  export function useState<T>(initial: T): [T, (value: T | ((prev: T) => T)) => void]
  export function useRef<T>(initial: T | null): { current: T | null }
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void
  export function useMemo<T>(factory: () => T, deps?: any[]): T
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any
    }
  }
}
