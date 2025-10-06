/// <reference types="vite/client" />

// Vue SFC shim so TS understands .vue imports
declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, any>
    export default component
  }