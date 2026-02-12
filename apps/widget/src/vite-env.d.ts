/// <reference types="vite/client" />

declare module 'preact/jsx-runtime' {
  import { JSX } from 'preact'
  
  export namespace JSX {
    interface IntrinsicElements extends preact.JSX.IntrinsicElements {}
  }
  
  export function jsx(type: any, props: any, key?: any): any
  export function jsxs(type: any, props: any, key?: any): any
  export function Fragment(props: { children?: any }): any
}

declare global {
  namespace JSX {
    interface IntrinsicElements extends preact.JSX.IntrinsicElements {}
  }
}