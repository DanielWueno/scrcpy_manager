import { app, BrowserWindow, shell } from "electron";
import { join } from "path";
import { spawn } from "child_process";
import __cjs_mod__ from "node:module";
const __filename = import.meta.filename;
const __dirname = import.meta.dirname;
const require2 = __cjs_mod__.createRequire(import.meta.url);
let apiProcess = null;
let mainWindow = null;
const isDev = !app.isPackaged;
const API_PORT = 59399;
function getApiExecutablePath() {
  return join(process.resourcesPath, "api", "Mobile.Remote.Toolkit.Api.exe");
}
async function waitForApi(maxAttempts = 30) {
  const healthUrl = `http://localhost:${API_PORT}/api/android/devices`;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const resp = await fetch(healthUrl);
      if (resp.status < 500) return true;
    } catch {
    }
    await new Promise((r) => setTimeout(r, 1e3));
  }
  return false;
}
async function startApi() {
  if (isDev) return;
  const apiExe = getApiExecutablePath();
  console.log("[Electron] Starting API:", apiExe);
  apiProcess = spawn(apiExe, [], {
    detached: false,
    stdio: "ignore",
    env: {
      ...process.env,
      ASPNETCORE_ENVIRONMENT: "Production",
      ASPNETCORE_URLS: `http://localhost:${API_PORT}`,
      ELECTRON_HOSTED: "1"
    }
  });
  apiProcess.on("error", (err) => {
    console.error("[Electron] API process error:", err);
  });
  apiProcess.on("exit", (code) => {
    console.log("[Electron] API process exited with code:", code);
  });
  console.log("[Electron] Waiting for API to be ready...");
  const ready = await waitForApi();
  if (!ready) {
    console.error("[Electron] API failed to start within 30 seconds");
  } else {
    console.log("[Electron] API is ready");
  }
}
function killApi() {
  if (apiProcess && !apiProcess.killed) {
    apiProcess.kill("SIGTERM");
    apiProcess = null;
  }
}
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 600,
    title: "Mobile Remote Toolkit",
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      // Allow loading local resources in production
      webSecurity: false
    },
    autoHideMenuBar: true,
    show: false
  });
  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();
  });
  if (isDev) {
    const devUrl = process.env["ELECTRON_RENDERER_URL"] || "http://localhost:3000";
    mainWindow.loadURL(devUrl);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
app.whenReady().then(async () => {
  await startApi();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
app.on("window-all-closed", () => {
  killApi();
  if (process.platform !== "darwin") {
    app.quit();
  }
});
app.on("before-quit", () => {
  killApi();
});
