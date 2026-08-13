import {
  app,
  BrowserWindow,
  shell,
  ipcMain,
  clipboard,
  nativeImage,
} from "electron";
import { join } from "path";
import { spawn, ChildProcess } from "child_process";
import * as http from "http";
import * as https from "https";
import { openMirrorWindow, closeMirrorWindow } from "./mirrorWindow";

let apiProcess: ChildProcess | null = null;
let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

const isDev = !app.isPackaged;
const API_PORT = 59399;

// Misma convencion que .env.development/.env.production del lado Vue: en dev la API
// corre con el certificado HTTPS de desarrollo de .NET (launchSettings.json), en prod
// se levanta explicitamente en HTTP (ver startApi() mas abajo).
function apiBaseUrl(): string {
  return isDev
    ? `https://localhost:${API_PORT}/api`
    : `http://localhost:${API_PORT}/api`;
}

// En dev la API corre con el certificado autofirmado de dotnet dev-certs - Chromium (el
// renderer, via axios) lo acepta porque en esta maquina ya esta confiado en el almacen de
// Windows, pero el proceso principal de Electron llama por Node puro (no pasa por el motor
// de red de Chromium), y Node no lee ese almacen de confianza del SO. Como este cliente HTTP
// solo habla con localhost (nunca un host externo ni uno provisto por el usuario), se
// desactiva la validacion de certificado solo para este agente puntual en vez de tocar la
// validacion TLS de todo el proceso.
const httpsAgent = new https.Agent({ rejectUnauthorized: false });

function postIOSAction(
  udid: string,
  action: string,
  payload: Record<string, unknown>,
): Promise<{ success: boolean; message?: string; error?: string }> {
  return new Promise((resolvePromise) => {
    const targetUrl = new URL(
      `${apiBaseUrl()}/ios/devices/${encodeURIComponent(udid)}/action`,
    );
    const body = JSON.stringify({ action, payload });
    const client = targetUrl.protocol === "https:" ? https : http;

    const req = client.request(
      targetUrl,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
        },
        agent: targetUrl.protocol === "https:" ? httpsAgent : undefined,
      },
      (res) => {
        let raw = "";
        res.on("data", (chunk) => (raw += chunk));
        res.on("end", () => {
          try {
            resolvePromise(JSON.parse(raw));
          } catch {
            resolvePromise({ success: false, error: `Respuesta invalida: ${raw}` });
          }
        });
      },
    );

    req.on("error", (error) => resolvePromise({ success: false, error: error.message }));
    req.write(body);
    req.end();
  });
}

// In dev mode the .NET API is run manually; in prod it's bundled in resources/api/
function getApiExecutablePath(): string {
  return join(process.resourcesPath, "api", "Mobile.Remote.Toolkit.Api.exe");
}

async function waitForApi(maxAttempts = 30): Promise<boolean> {
  const healthUrl = `http://localhost:${API_PORT}/api/android/devices`;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const resp = await fetch(healthUrl);
      if (resp.status < 500) return true;
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  return false;
}

async function startApi(): Promise<void> {
  if (isDev) return; // In dev, developer runs API manually

  const apiExe = getApiExecutablePath();
  console.log("[Electron] Starting API:", apiExe);

  apiProcess = spawn(apiExe, [], {
    // Sin esto, ASP.NET Core usa el cwd del proceso que lo lanza (Electron) como content root
    // para ubicar appsettings.json - en una instalacion real ese cwd no es la carpeta del .exe
    // (depende de desde donde Windows abrio el acceso directo), asi que appsettings.json no se
    // encontraba y IOS:Mirror:Mode caia al default "external".
    cwd: join(process.resourcesPath, "api"),
    detached: false,
    stdio: "ignore",
    env: {
      ...process.env,
      ASPNETCORE_ENVIRONMENT: "Production",
      ASPNETCORE_URLS: `http://localhost:${API_PORT}`,
      ELECTRON_HOSTED: "1",
    },
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

function killApi(): void {
  if (apiProcess && !apiProcess.killed) {
    apiProcess.kill("SIGTERM");
    apiProcess = null;
  }
}

// Se muestra de inmediato al abrir la app (antes de esperar la API .NET y de cargar el
// renderer) para que el doble-clic tenga feedback visual instantaneo - sin esto, mientras
// startApi() espera hasta 30s, no aparece nada en pantalla y parece que la app no abrio.
function createSplashWindow(): void {
  splashWindow = new BrowserWindow({
    width: 320,
    height: 180,
    frame: false,
    resizable: false,
    movable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    show: true,
    backgroundColor: "#1e1e2e",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  splashWindow.loadURL(
    "data:text/html;charset=utf-8," +
      encodeURIComponent(`<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; height: 100%; background: #1e1e2e; overflow: hidden;
    display: flex; align-items: center; justify-content: center; flex-direction: column;
    font-family: "Segoe UI", sans-serif; color: #cdd6f4; }
  .spinner { width: 36px; height: 36px; border-radius: 50%;
    border: 3px solid rgba(205, 214, 244, 0.2); border-top-color: #89b4fa;
    animation: spin 0.8s linear infinite; margin-bottom: 14px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  p { margin: 0; font-size: 13px; opacity: 0.85; }
</style>
</head>
<body>
  <div class="spinner"></div>
  <p>Iniciando Mobile Remote Toolkit...</p>
</body>
</html>`),
  );

  splashWindow.on("closed", () => {
    splashWindow = null;
  });
}

function closeSplashWindow(): void {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.close();
  }
  splashWindow = null;
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 600,
    title: "Mobile Remote Toolkit - powered by Wueno BP",
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      // Allow loading local resources in production
      webSecurity: false,
    },
    autoHideMenuBar: true,
    show: false,
  });

  mainWindow.once("ready-to-show", () => {
    closeSplashWindow();
    mainWindow?.show();
  });

  // Si la carga falla (p. ej. falta un asset), "ready-to-show" nunca dispara y el splash
  // se quedaria girando para siempre - mejor mostrar la ventana (aunque este en blanco)
  // que dejar al usuario viendo un splash colgado sin ningun indicio del error.
  mainWindow.webContents.on("did-fail-load", (_event, errorCode, errorDescription) => {
    console.error("[Electron] did-fail-load:", errorCode, errorDescription);
    closeSplashWindow();
    mainWindow?.show();
  });

  if (isDev) {
    const devUrl =
      process.env["ELECTRON_RENDERER_URL"] || "http://localhost:3000";
    mainWindow.loadURL(devUrl);
    mainWindow.webContents.openDevTools();
    mainWindow.webContents.on("console-message", (_e, _level, message) => {
      console.log("[renderer]", message);
    });
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }

  // Open external links in the default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  createSplashWindow();
  await startApi();
  createWindow();

  // ── IPC: iOS mirror (go-ios MJPEG) in its own floating window, like scrcpy ──
  ipcMain.handle(
    "mirror:open",
    (_event, url: string, title: string, udid: string) => {
      console.log("[mirror:open] received", { url, title, udid });
      openMirrorWindow(url, title, udid);
      return { success: true };
    },
  );

  ipcMain.handle("mirror:close", () => {
    closeMirrorWindow();
    return { success: true };
  });

  // Control tactil real (DeviceKit via IOSControlService) - la ventana del mirror no
  // tiene su propio origen http (es una pagina data:), asi que estas llamadas van por IPC
  // en vez de fetch() directo desde el renderer para no depender de la config de CORS.
  ipcMain.handle(
    "mirror:tap",
    (_event, udid: string, x: number, y: number) =>
      postIOSAction(udid, "tap", { x, y }),
  );

  ipcMain.handle(
    "mirror:swipe",
    (
      _event,
      udid: string,
      fromX: number,
      fromY: number,
      toX: number,
      toY: number,
      durationMs: number,
    ) =>
      postIOSAction(udid, "swipe", {
        from_x: fromX,
        from_y: fromY,
        to_x: toX,
        to_y: toY,
        duration_ms: durationMs,
      }),
  );

  ipcMain.handle(
    "mirror:swipe-path",
    (
      _event,
      udid: string,
      points: { x: number; y: number; t: number }[],
    ) => postIOSAction(udid, "swipe", { points }),
  );

  ipcMain.handle(
    "mirror:longpress",
    (_event, udid: string, x: number, y: number, durationMs: number) =>
      postIOSAction(udid, "long_press", { x, y, duration_ms: durationMs }),
  );

  ipcMain.handle(
    "mirror:button",
    (_event, udid: string, name: string) =>
      postIOSAction(udid, "button", { name }),
  );

  ipcMain.handle("mirror:screenshot", (_event, udid: string) =>
    postIOSAction(udid, "screenshot", {}),
  );
  // ──────────────────────────────────────────────────────────────────────────

  ipcMain.handle("clipboard:copy-image-path", (_event, filePath: string) => {
    try {
      if (!filePath || typeof filePath !== "string") {
        return { success: false, error: "Ruta de imagen inválida" };
      }

      const image = nativeImage.createFromPath(filePath);
      if (image.isEmpty()) {
        return { success: false, error: "No se pudo cargar la imagen" };
      }

      clipboard.writeImage(image);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Error desconocido",
      };
    }
  });
  // ──────────────────────────────────────────────────────────────────────────

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
