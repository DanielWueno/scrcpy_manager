/**
 * mirrorWindow.ts
 * Opens the iOS mirror (go-ios MJPEG stream) in its own free-floating
 * BrowserWindow, instead of embedding it inside the main app view.
 *
 * Unlike Android/scrcpy (a real external process with its own OS window that
 * we dock next to), go-ios's "screenshot --stream" is headless - it never
 * opens a window, it just serves HTTP. So the "own window" here is one we
 * create ourselves, pointed at that MJPEG URL, so the user can move/resize
 * it freely just like they already do with the scrcpy window.
 */

import { BrowserWindow } from "electron";

let mirrorWindow: BrowserWindow | null = null;

function buildMirrorHtml(streamUrl: string, title: string): string {
  // Plain HTML/JS (no Vue/build step) - this window is content-independent
  // from the renderer bundle. multipart/x-mixed-replace refreshes a plain
  // <img> natively in Chromium, no extra JS needed for the happy path; the
  // retry loop only covers the stream not being up yet right after start.
  const escapedUrl = JSON.stringify(streamUrl);
  const escapedTitle = title.replace(/[<>&]/g, "");
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${escapedTitle}</title>
<style>
  html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
  #mirror { display: block; width: 100%; height: 100%; object-fit: contain; }
  #status { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    color: #fff; font: 14px sans-serif; text-align: center; padding: 16px; }
</style>
</head>
<body>
  <img id="mirror" />
  <div id="status">Conectando al mirror...</div>
  <script>
    const url = ${escapedUrl};
    const img = document.getElementById("mirror");
    const status = document.getElementById("status");
    const MAX_RETRIES = 8;
    let attempt = 0;

    function connect() {
      status.textContent = attempt === 0 ? "Conectando al mirror..." : "Reintentando conexion...";
      status.style.display = "flex";
      const sep = url.includes("?") ? "&" : "?";
      img.src = url + sep + "retry=" + attempt;
    }

    img.addEventListener("load", () => {
      status.style.display = "none";
      attempt = 0;
    });

    img.addEventListener("error", () => {
      if (attempt >= MAX_RETRIES) {
        status.textContent = "No se pudo conectar al mirror (" + url + ")";
        return;
      }
      attempt += 1;
      setTimeout(connect, 1000);
    });

    connect();
  </script>
</body>
</html>`;
}

/**
 * Open (or focus, if already open) the floating mirror window for the given
 * MJPEG stream URL.
 */
export function openMirrorWindow(streamUrl: string, title: string): void {
  if (mirrorWindow && !mirrorWindow.isDestroyed()) {
    mirrorWindow.loadURL(
      `data:text/html,${encodeURIComponent(buildMirrorHtml(streamUrl, title))}`,
    );
    mirrorWindow.focus();
    return;
  }

  mirrorWindow = new BrowserWindow({
    width: 420,
    height: 860,
    title,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mirrorWindow.loadURL(
    `data:text/html,${encodeURIComponent(buildMirrorHtml(streamUrl, title))}`,
  );

  mirrorWindow.on("closed", () => {
    mirrorWindow = null;
  });
}

/** Close the floating mirror window, if open (no-op otherwise). */
export function closeMirrorWindow(): void {
  if (mirrorWindow && !mirrorWindow.isDestroyed()) {
    mirrorWindow.close();
  }
  mirrorWindow = null;
}
