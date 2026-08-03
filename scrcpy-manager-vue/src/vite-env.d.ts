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
  open(url: string, title: string): Promise<{ success: boolean }>;
  close(): Promise<{ success: boolean }>;
}

declare interface Window {
  dockApi?: DockApi;
  clipboardApi?: ClipboardApi;
  mirrorApi?: MirrorApi;
}
