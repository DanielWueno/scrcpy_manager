/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_SIGNALR_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
interface DockApi {
  attach(
    serial: string,
    platform?: string,
  ): Promise<{ success: boolean; error?: string }>;
  detach(): Promise<{ success: boolean }>;
}

interface ClipboardApi {
  copyImagePath(
    filePath: string,
  ): Promise<{ success: boolean; error?: string }>;
}

interface MirrorApi {
  open(url: string, title: string, udid: string): Promise<{ success: boolean }>;
  close(): Promise<{ success: boolean }>;
}

// Solo se usa dentro del contenido inline de electron/main/mirrorWindow.ts (misma
// ventana, mismo preload) - no se llama desde el resto de la app Vue.
interface MirrorControlApi {
  tap(udid: string, x: number, y: number): Promise<{ success: boolean; error?: string }>;
  swipe(
    udid: string,
    fromX: number,
    fromY: number,
    toX: number,
    toY: number,
    durationMs: number,
  ): Promise<{ success: boolean; error?: string }>;
  swipePath(
    udid: string,
    points: { x: number; y: number; t: number }[],
  ): Promise<{ success: boolean; error?: string }>;
  longPress(
    udid: string,
    x: number,
    y: number,
    durationMs: number,
  ): Promise<{ success: boolean; error?: string }>;
  button(udid: string, name: string): Promise<{ success: boolean; error?: string }>;
}

declare interface Window {
  dockApi?: DockApi;
  clipboardApi?: ClipboardApi;
  mirrorApi?: MirrorApi;
  mirrorControlApi?: MirrorControlApi;
}
