/**
 * mirrorWindow.ts
 * Opens the iOS mirror (go-ios/DeviceKit h264 stream) in its own free-floating
 * BrowserWindow, instead of embedding it inside the main app view.
 *
 * Unlike Android/scrcpy (a real external process with its own OS window that
 * we dock next to), go-ios is headless - it never opens a window, it just
 * serves HTTP. So the "own window" here is one we create ourselves, decoding
 * the raw H264 Annex-B stream with WebCodecs onto a <canvas> (no <img>/MJPEG
 * here - DeviceKit's stream is real h264, not multipart/x-mixed-replace), so
 * the user can move/resize it freely just like they already do with scrcpy.
 * The same canvas also captures pointer gestures and forwards them as
 * tap/swipe/long_press via IPC (see electron/preload/index.ts, mirrorControlApi).
 */

import { app, BrowserWindow } from "electron";
import { join } from "path";
import { writeFileSync } from "fs";

let mirrorWindow: BrowserWindow | null = null;

// WebCodecs (VideoDecoder) solo esta disponible en un contexto seguro, y un data: URL
// tiene origen opaco - Chromium no lo trata como seguro, asi que VideoDecoder ni existe
// ahi (confirmado: "ReferenceError: VideoDecoder is not defined" corriendo como data:).
// file:// si se trata como contexto seguro, por eso se escribe el HTML a un archivo
// temporal en vez de cargarlo inline.
const MIRROR_HTML_PATH = join(app.getPath("temp"), "mrt-mirror-window.html");

function buildMirrorHtml(streamUrl: string, title: string, udid: string): string {
  const escapedUrl = JSON.stringify(streamUrl);
  const escapedUdid = JSON.stringify(udid);
  const escapedTitle = title.replace(/[<>&]/g, "");
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${escapedTitle}</title>
<style>
  html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
  #wrap { position: relative; width: 100%; height: 100%; }
  #mirror { display: block; width: 100%; height: 100%; object-fit: contain; touch-action: none; }
  #status { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    color: #fff; font: 14px sans-serif; text-align: center; padding: 16px; pointer-events: none; }
  #buttons { position: absolute; left: 0; right: 0; bottom: 0; display: flex; justify-content: center;
    gap: 8px; padding: 8px; background: rgba(0, 0, 0, 0.35); transition: opacity 0.15s; }
  #buttons.hidden { display: none; }
  #buttons button { flex: 0 0 auto; padding: 6px 12px; font: 12px sans-serif; color: #fff;
    background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px; cursor: pointer; }
  #buttons button:active { background: rgba(255, 255, 255, 0.35); }
  /* Boton para ocultar/mostrar la barra de acciones antes de grabar pantalla (asi no
     queda esa barra pegada en la grabacion). Discreto por default: opaco solo al hover. */
  #toggleBar { position: absolute; top: 8px; right: 8px; z-index: 10; padding: 4px 8px;
    font: 11px sans-serif; color: #fff; background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 6px; cursor: pointer;
    opacity: 0.35; transition: opacity 0.15s; }
  #toggleBar:hover { opacity: 1; }
  #toast { position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.65); color: #fff; font: 12px sans-serif; padding: 6px 12px;
    border-radius: 6px; opacity: 0; pointer-events: none; transition: opacity 0.2s; z-index: 10; }
  #toast.show { opacity: 1; }
</style>
</head>
<body>
  <div id="wrap">
    <canvas id="mirror"></canvas>
    <div id="status">Conectando al mirror...</div>
    <div id="toast"></div>
    <button id="toggleBar" title="Ocultar/mostrar acciones rapidas">Ocultar</button>
    <div id="buttons">
      <button data-button="home">Home</button>
      <button data-button="volumeDown">Vol-</button>
      <button data-button="volumeUp">Vol+</button>
      <button data-button="lock">Lock</button>
      <button data-action="screenshot">Captura</button>
    </div>
  </div>
  <script>
    const streamUrl = ${escapedUrl};
    const udid = ${escapedUdid};
    const canvas = document.getElementById("mirror");
    const ctx = canvas.getContext("2d");
    const status = document.getElementById("status");

    function setStatus(text) {
      status.textContent = text || "";
      status.style.display = text ? "flex" : "none";
    }

    // ── H264 Annex-B parsing + WebCodecs decode ────────────────────────────
    let decoder = null;
    let videoWidth = 0;
    let videoHeight = 0;
    let reconnectAttempt = 0;
    const MAX_RETRIES = 8;
    let stopped = false;

    function buildCodecString(nalHeaderAndSps) {
      // nalHeaderAndSps[0] is the NAL header byte itself; profile/constraints/level
      // follow immediately per the H.264 SPS layout.
      const hex = (n) => n.toString(16).padStart(2, "0");
      return "avc1." + hex(nalHeaderAndSps[1]) + hex(nalHeaderAndSps[2]) + hex(nalHeaderAndSps[3]);
    }

    function ensureCanvasSize(frame) {
      if (frame.displayWidth !== videoWidth || frame.displayHeight !== videoHeight) {
        videoWidth = frame.displayWidth;
        videoHeight = frame.displayHeight;
        canvas.width = videoWidth;
        canvas.height = videoHeight;
      }
    }

    function onDecodedFrame(frame) {
      ensureCanvasSize(frame);
      ctx.drawImage(frame, 0, 0, videoWidth, videoHeight);
      frame.close();
      setStatus("");
    }

    function makeDecoder(codecString) {
      const d = new VideoDecoder({
        output: onDecodedFrame,
        error: (e) => scheduleReconnect("decoder error: " + e),
      });
      d.configure({ codec: codecString, avc: { format: "annexb" }, optimizeForLatency: true });
      return d;
    }

    let timestampUs = 0;
    const FRAME_DURATION_US = Math.round(1e6 / 30);

    function decodeAccessUnit(bytes, containsSps, isKeyFrame) {
      if (!decoder && containsSps) {
        try {
          decoder = makeDecoder(buildCodecString(bytes.subarray(findFirstSpsOffset(bytes))));
        } catch (e) {
          scheduleReconnect("makeDecoder threw: " + e);
          return;
        }
      }
      if (!decoder) return; // esperando el primer SPS para poder configurar el decoder

      timestampUs += FRAME_DURATION_US;
      try {
        decoder.decode(
          new EncodedVideoChunk({
            type: isKeyFrame ? "key" : "delta",
            timestamp: timestampUs,
            data: bytes,
          }),
        );
      } catch (e) {
        scheduleReconnect("decoder.decode threw: " + e);
      }
    }

    function findFirstSpsOffset(buf) {
      const starts = scanStartCodes(buf, 0);
      for (const s of starts) {
        if ((buf[s] & 0x1f) === 7) return s;
      }
      return 0;
    }

    function scanStartCodes(buf, fromIdx) {
      const found = [];
      for (let i = fromIdx; i + 2 < buf.length; i++) {
        if (buf[i] === 0 && buf[i + 1] === 0 && buf[i + 2] === 1) {
          found.push(i + 3); // offset of the NAL header byte itself
          i += 2;
        }
      }
      return found;
    }

    // Agrupa NALs en unidades de acceso: junta cualquier SPS/PPS/SEI que preceda a un
    // slice (tipo 1 o 5) con ese mismo slice - asi el keyframe (SPS+PPS+SEI+IDR, tal
    // como los emite DeviceKit) se decodifica como un solo chunk.
    let buffer = new Uint8Array(0);
    let nalStarts = []; // offsets del byte de header NAL (ya sin el start code)
    let groupBeginStart = 0; // offset (con start code incluido) del primer NAL sin flushear
    let groupHasSps = false;
    let groupHasKeyFrame = false;

    function trimBuffer() {
      if (groupBeginStart < 4096) return;
      buffer = buffer.slice(groupBeginStart);
      nalStarts = nalStarts.map((n) => n - groupBeginStart);
      groupBeginStart = 0;
    }

    function feed(chunk) {
      const merged = new Uint8Array(buffer.length + chunk.length);
      merged.set(buffer, 0);
      merged.set(chunk, buffer.length);
      const scanFrom = Math.max(0, buffer.length - 3);
      buffer = merged;
      for (const s of scanStartCodes(buffer, scanFrom)) {
        if (!nalStarts.includes(s)) nalStarts.push(s);
      }

      while (nalStarts.length >= 2) {
        const nalHeaderOffset = nalStarts[0];
        const nalEnd = nalStarts[1] - 3; // excluye el start code del siguiente NAL
        const type = buffer[nalHeaderOffset] & 0x1f;

        if (type === 7) groupHasSps = true;
        if (type === 1 || type === 5) {
          if (type === 5) groupHasKeyFrame = true;
          const accessUnit = buffer.slice(groupBeginStart, nalEnd);
          decodeAccessUnit(accessUnit, groupHasSps, groupHasKeyFrame);
          groupBeginStart = nalEnd;
          groupHasSps = false;
          groupHasKeyFrame = false;
        }

        nalStarts.shift();
      }
      trimBuffer();
    }

    function resetParserState() {
      buffer = new Uint8Array(0);
      nalStarts = [];
      groupBeginStart = 0;
      groupHasSps = false;
      groupHasKeyFrame = false;
      timestampUs = 0;
      if (decoder) {
        try { decoder.close(); } catch (e) {}
        decoder = null;
      }
    }

    let reconnectTimer = null;
    function scheduleReconnect(reason) {
      console.error("[mirror] reconnect scheduled, reason:", reason);
      if (stopped || reconnectTimer) return;
      resetParserState();
      reconnectAttempt += 1;
      if (reconnectAttempt > MAX_RETRIES) {
        setStatus("No se pudo conectar al mirror (" + streamUrl + ")");
        return;
      }
      setStatus("Reintentando conexion (" + reconnectAttempt + ")...");
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        connect();
      }, 1000);
    }

    async function connect() {
      setStatus(reconnectAttempt === 0 ? "Conectando al mirror..." : "Reintentando conexion...");
      try {
        const sep = streamUrl.includes("?") ? "&" : "?";
        const response = await fetch(streamUrl + sep + "t=" + Date.now());
        if (!response.ok || !response.body) throw new Error("HTTP " + response.status);
        reconnectAttempt = 0;
        const reader = response.body.getReader();
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          feed(value);
        }
        throw new Error("stream ended");
      } catch (e) {
        scheduleReconnect("connect() caught: " + (e && e.stack || e));
      }
    }

    connect();

    // ── Gestos: tap / swipe / long-press, traducidos a coordenadas de pantalla ─
    // El coordinate space de device.io.tap/swipe coincide con la resolucion del
    // video (confirmado contra un iPad real: screenSize de device.info y el
    // tamaño decodificado del stream son el mismo, 744x1133 vs 744x1132), asi que
    // no hace falta un factor de escala aparte del letterboxing del propio canvas.
    const LONG_PRESS_MS = 500;
    const MOVE_THRESHOLD_PX = 12;
    let gesture = null; // { pointerId, startX, startY, startTime, longPressTimer, longPressFired }

    function toDeviceCoords(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      if (!videoWidth || !videoHeight || rect.width === 0 || rect.height === 0) return null;

      const scale = Math.min(rect.width / videoWidth, rect.height / videoHeight);
      const renderedWidth = videoWidth * scale;
      const renderedHeight = videoHeight * scale;
      const offsetX = (rect.width - renderedWidth) / 2;
      const offsetY = (rect.height - renderedHeight) / 2;

      const x = (clientX - rect.left - offsetX) / scale;
      const y = (clientY - rect.top - offsetY) / scale;
      // Clampear en vez de descartar: si el drag de un swipe termina fuera del canvas
      // (comun al "tirar" hacia el borde de la ventana), sin esto toDeviceCoords devolvia
      // null y el pointerup caia al fallback de start=end, convirtiendo el swipe en un tap.
      return {
        x: Math.min(Math.max(x, 0), videoWidth),
        y: Math.min(Math.max(y, 0), videoHeight),
      };
    }

    canvas.addEventListener("pointerdown", (event) => {
      const point = toDeviceCoords(event.clientX, event.clientY);
      if (!point) return;
      canvas.setPointerCapture(event.pointerId);

      gesture = {
        pointerId: event.pointerId,
        startX: point.x,
        startY: point.y,
        startTime: performance.now(),
        longPressFired: false,
        // Ruta real del arrastre (no solo start/end) - se manda tal cual a DeviceKit para
        // que el gesto reproducido siga la forma y velocidad reales del drag, en vez de una
        // linea recta interpolada entre dos puntos.
        path: [{ x: point.x, y: point.y, t: 0 }],
        lastPathTime: 0,
        longPressTimer: setTimeout(() => {
          if (!gesture) return;
          gesture.longPressFired = true;
          window.mirrorControlApi?.longPress(udid, gesture.startX, gesture.startY, LONG_PRESS_MS);
        }, LONG_PRESS_MS),
      };
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!gesture || gesture.pointerId !== event.pointerId) return;
      const point = toDeviceCoords(event.clientX, event.clientY);
      if (!point) return;
      const distance = Math.hypot(point.x - gesture.startX, point.y - gesture.startY);
      // Un swipe lento (o con una pausa) que dure mas de LONG_PRESS_MS disparaba el long-press
      // en el punto inicial y el pointerup descartaba el swipe entero (wasLongPress). Cancelar
      // el timer en cuanto se detecta arrastre real evita que un swipe se coma como long-press.
      if (gesture.longPressTimer && distance > MOVE_THRESHOLD_PX) {
        clearTimeout(gesture.longPressTimer);
        gesture.longPressTimer = null;
      }

      // Throttle a ~60fps (por tiempo, no por cantidad de eventos) para no acumular un path
      // gigante en un drag lento y largo.
      const t = performance.now() - gesture.startTime;
      if (t - gesture.lastPathTime >= 16) {
        gesture.path.push({ x: point.x, y: point.y, t });
        gesture.lastPathTime = t;
      }
    });

    canvas.addEventListener("pointerup", (event) => {
      if (!gesture || gesture.pointerId !== event.pointerId) return;
      clearTimeout(gesture.longPressTimer);
      const wasLongPress = gesture.longPressFired;
      const start = gesture;
      gesture = null;
      if (wasLongPress) return;

      const point = toDeviceCoords(event.clientX, event.clientY) || { x: start.startX, y: start.startY };
      const dx = point.x - start.startX;
      const dy = point.y - start.startY;
      const distance = Math.hypot(dx, dy);

      if (distance <= MOVE_THRESHOLD_PX) {
        window.mirrorControlApi?.tap(udid, start.startX, start.startY);
      } else {
        const t = performance.now() - start.startTime;
        const path = start.path.slice();
        const last = path[path.length - 1];
        if (last.x !== point.x || last.y !== point.y || last.t !== t) {
          path.push({ x: point.x, y: point.y, t });
        }
        window.mirrorControlApi?.swipePath(udid, path);
      }
    });

    canvas.addEventListener("pointercancel", () => {
      if (gesture) clearTimeout(gesture.longPressTimer);
      gesture = null;
    });

    document.getElementById("buttons").addEventListener("click", (event) => {
      const name = event.target?.dataset?.button;
      if (name) {
        window.mirrorControlApi?.button(udid, name);
        return;
      }
      if (event.target?.dataset?.action === "screenshot") takeScreenshot();
    });

    const toast = document.getElementById("toast");
    let toastTimer = null;
    function showToast(text) {
      toast.textContent = text;
      toast.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove("show"), 1500);
    }

    async function takeScreenshot() {
      const result = await window.mirrorControlApi?.screenshot(udid);
      showToast(result?.success ? "Captura guardada" : (result?.message || result?.error || "Error al capturar"));
    }

    // Oculta la barra de acciones (Home/Vol/Lock/Captura) para que no aparezca al grabar
    // la pantalla con otra herramienta - visible por default, el usuario la oculta cuando
    // la necesite.
    const buttonsBar = document.getElementById("buttons");
    const toggleBar = document.getElementById("toggleBar");
    toggleBar.addEventListener("click", () => {
      const hidden = buttonsBar.classList.toggle("hidden");
      toggleBar.textContent = hidden ? "Mostrar" : "Ocultar";
    });

    window.addEventListener("beforeunload", () => {
      stopped = true;
      if (gesture) clearTimeout(gesture.longPressTimer);
      resetParserState();
    });
  </script>
</body>
</html>`;
}

/**
 * Open (or focus, if already open) the floating mirror window for the given
 * device (h264 stream URL from DeviceKit, plus its udid for gesture forwarding).
 */
export function openMirrorWindow(streamUrl: string, title: string, udid: string): void {
  const html = buildMirrorHtml(streamUrl, title, udid);
  writeFileSync(MIRROR_HTML_PATH, html, "utf-8");

  if (mirrorWindow && !mirrorWindow.isDestroyed()) {
    mirrorWindow.loadFile(MIRROR_HTML_PATH);
    mirrorWindow.focus();
    return;
  }

  mirrorWindow = new BrowserWindow({
    width: 420,
    height: 860,
    title,
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      // DeviceKit (servidor Go en 127.0.0.1:12004) no manda headers CORS - sin esto, el
      // fetch() del stream h264 se bloquea por CORS y nunca conecta (mismo ajuste que ya
      // tiene mainWindow).
      webSecurity: false,
    },
  });

  mirrorWindow.webContents.on("console-message", (_e, _level, message) => {
    console.log("[mirror-window]", message);
  });

  mirrorWindow.loadFile(MIRROR_HTML_PATH);

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
