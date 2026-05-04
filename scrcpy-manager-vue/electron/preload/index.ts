import { contextBridge } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

// Expose safe electron APIs to the renderer process
contextBridge.exposeInMainWorld("electron", electronAPI);
