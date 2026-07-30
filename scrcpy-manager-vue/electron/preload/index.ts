import { contextBridge, ipcRenderer } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

// Expose safe electron APIs to the renderer process
contextBridge.exposeInMainWorld("electron", electronAPI);

// Expose dock API to Vue renderer
contextBridge.exposeInMainWorld("dockApi", {
  attach: (serial: string, platform?: string) =>
    ipcRenderer.invoke("dock:attach", serial, platform),
  detach: () => ipcRenderer.invoke("dock:detach"),
});

contextBridge.exposeInMainWorld("clipboardApi", {
  copyImagePath: (filePath: string) =>
    ipcRenderer.invoke("clipboard:copy-image-path", filePath),
});
