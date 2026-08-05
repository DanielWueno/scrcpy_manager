import { contextBridge, ipcRenderer } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

// Expose safe electron APIs to the renderer process
contextBridge.exposeInMainWorld("electron", electronAPI);

contextBridge.exposeInMainWorld("clipboardApi", {
  copyImagePath: (filePath: string) =>
    ipcRenderer.invoke("clipboard:copy-image-path", filePath),
});

// Floating mirror window (iOS/go-ios) - independent of the main app window
contextBridge.exposeInMainWorld("mirrorApi", {
  open: (url: string, title: string, udid: string) =>
    ipcRenderer.invoke("mirror:open", url, title, udid),
  close: () => ipcRenderer.invoke("mirror:close"),
});

// Control tactil real (DeviceKit) para el contenido de la ventana del mirror - ver
// electron/main/mirrorWindow.ts. Mismo preload que la ventana principal (sin entry
// separado en electron.vite.config.ts), asi que estas quedan disponibles ahi tambien
// aunque no se usen fuera del mirror.
contextBridge.exposeInMainWorld("mirrorControlApi", {
  tap: (udid: string, x: number, y: number) =>
    ipcRenderer.invoke("mirror:tap", udid, x, y),
  swipe: (
    udid: string,
    fromX: number,
    fromY: number,
    toX: number,
    toY: number,
    durationMs: number,
  ) => ipcRenderer.invoke("mirror:swipe", udid, fromX, fromY, toX, toY, durationMs),
  swipePath: (udid: string, points: { x: number; y: number; t: number }[]) =>
    ipcRenderer.invoke("mirror:swipe-path", udid, points),
  longPress: (udid: string, x: number, y: number, durationMs: number) =>
    ipcRenderer.invoke("mirror:longpress", udid, x, y, durationMs),
  button: (udid: string, name: string) =>
    ipcRenderer.invoke("mirror:button", udid, name),
  screenshot: (udid: string) => ipcRenderer.invoke("mirror:screenshot", udid),
});
