/**
 * windowManager.ts
 * Docks the Electron control-panel window alongside the scrcpy mirror window.
 *
 * Flow:
 *  1. scrcpy is launched with  --window-title "MRT-{serial}"
 *  2. Renderer calls IPC  "dock:attach" with the serial
 *  3. We poll User32 until FindWindowW returns a valid HWND
 *  4. We read scrcpy's rect and reposition the Electron window to the right of it
 *  5. A periodic sync keeps both windows aligned while the user moves scrcpy
 *  6. IPC "dock:detach" stops syncing and restores the Electron window to its default size
 */

import koffi from "koffi";
import { BrowserWindow } from "electron";

// ──────────────────────────────────────────────────────────────────────────────
// Win32 structs / types
// ──────────────────────────────────────────────────────────────────────────────

const RECT = koffi.struct("RECT", {
  left: "int32",
  top: "int32",
  right: "int32",
  bottom: "int32",
});

// user32.dll
const user32 = koffi.load("user32.dll");

const FindWindowW = user32.func("__stdcall", "FindWindowW", "void*", [
  "str16",
  "str16",
]);
const GetWindowRect = user32.func("__stdcall", "GetWindowRect", "bool", [
  "void*",
  koffi.out(koffi.pointer(RECT)),
]);
const SetWindowPos = user32.func("__stdcall", "SetWindowPos", "bool", [
  "void*",
  "void*",
  "int32",
  "int32",
  "int32",
  "int32",
  "uint32",
]);
const IsWindowVisible = user32.func("__stdcall", "IsWindowVisible", "bool", [
  "void*",
]);

// SetWindowPos flags
const SWP_NOSIZE = 0x0001; // eslint-disable-line @typescript-eslint/no-unused-vars
const SWP_NOMOVE = 0x0002; // eslint-disable-line @typescript-eslint/no-unused-vars
const SWP_NOZORDER = 0x0004;
const SWP_NOACTIVATE = 0x0010;
const SWP_SHOWWINDOW = 0x0040; // eslint-disable-line @typescript-eslint/no-unused-vars

// ──────────────────────────────────────────────────────────────────────────────
// State
// ──────────────────────────────────────────────────────────────────────────────

let syncInterval: ReturnType<typeof setInterval> | null = null;
let lastScrcpyRect = { left: 0, top: 0, right: 0, bottom: 0 };

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Build the window title used by scrcpy.
 * Must match the --window-title arg passed at launch.
 */
export function scrcpyWindowTitle(serial: string): string {
  return `MRT-${serial}`;
}

function getWindowRect(hwnd: unknown): typeof lastScrcpyRect | null {
  const rect = [{ left: 0, top: 0, right: 0, bottom: 0 }];
  const ok = GetWindowRect(hwnd, rect);
  if (!ok) return null;
  return rect[0];
}

/** Wait up to `timeoutMs` for a window with the given title to appear. */
async function waitForWindow(
  title: string,
  timeoutMs = 8000,
): Promise<unknown | null> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const hwnd = FindWindowW(null, title);
    if (hwnd && IsWindowVisible(hwnd)) return hwnd;
    await new Promise((r) => setTimeout(r, 300));
  }
  // Timeout — log for diagnostics
  console.warn(
    "[WindowManager] Timeout buscando ventana scrcpy con título:",
    title,
  );
  return null;
}

/**
 * Return the Electron window's HWND as a BigInt.
 * koffi v2.4+ accepts BigInt as a void* argument directly.
 * getNativeWindowHandle() returns a 4-byte Buffer on 32-bit and 8-byte on 64-bit.
 */
function getElectronHwndValue(win: BrowserWindow): bigint {
  const buf = win.getNativeWindowHandle();
  if (buf.length >= 8) return buf.readBigUInt64LE(0);
  return BigInt(buf.readUInt32LE(0));
}

// ──────────────────────────────────────────────────────────────────────────────
// Core: sync position
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Repositions the Electron window to the immediate right of the scrcpy window.
 * Matches scrcpy's height.
 */
function syncWindows(
  scrcpyHwnd: unknown,
  electronHwnd: bigint,
  panelWidth: number,
): void {
  const sr = getWindowRect(scrcpyHwnd);
  if (!sr) return;

  // Only reposition if scrcpy actually moved / changed size
  if (
    sr.left === lastScrcpyRect.left &&
    sr.top === lastScrcpyRect.top &&
    sr.right === lastScrcpyRect.right &&
    sr.bottom === lastScrcpyRect.bottom
  )
    return;

  lastScrcpyRect = { ...sr };

  const scrcpyHeight = sr.bottom - sr.top;
  const panelX = sr.right; // Dock to the right of scrcpy
  const panelY = sr.top;
  const panelH = scrcpyHeight;

  // Move Electron window (SWP_NOZORDER keeps current z-order, SWP_NOACTIVATE avoids stealing focus)
  SetWindowPos(
    electronHwnd,
    null,
    panelX,
    panelY,
    panelWidth,
    panelH,
    SWP_NOZORDER | SWP_NOACTIVATE,
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Public API
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Attach the Electron window alongside the scrcpy window for `serial`.
 * Returns true if the scrcpy window was found, false on timeout.
 */
export async function attachToMirror(
  win: BrowserWindow,
  serial: string,
): Promise<boolean> {
  // Stop any previous sync
  detachFromMirror();

  const title = scrcpyWindowTitle(serial);
  console.log("[WindowManager] Buscando ventana scrcpy:", title);

  let scrcpyHwnd: unknown;
  try {
    scrcpyHwnd = await waitForWindow(title, 10000);
  } catch (err) {
    console.error("[WindowManager] Error en FindWindowW:", err);
    return false;
  }

  if (!scrcpyHwnd) {
    console.warn(
      "[WindowManager] Ventana scrcpy NO encontrada (timeout 10 s). Título buscado:",
      title,
    );
    return false;
  }

  console.log(
    "[WindowManager] Ventana scrcpy encontrada, haciendo dock. HWND=",
    scrcpyHwnd,
  );

  let electronHwnd: bigint;
  try {
    electronHwnd = getElectronHwndValue(win);
    console.log("[WindowManager] Electron HWND=", electronHwnd.toString(16));
  } catch (err) {
    console.error("[WindowManager] Error obteniendo HWND de Electron:", err);
    return false;
  }

  // Panel width – the Electron control panel
  const PANEL_WIDTH = win.getBounds().width;

  // Initial sync
  lastScrcpyRect = { left: 0, top: 0, right: 0, bottom: 0 }; // force first sync
  try {
    syncWindows(scrcpyHwnd, electronHwnd, PANEL_WIDTH);
  } catch (err) {
    console.error("[WindowManager] Error en syncWindows inicial:", err);
    return false;
  }

  // Keep syncing every 150 ms
  syncInterval = setInterval(() => {
    try {
      // Stop if scrcpy was closed
      if (!IsWindowVisible(scrcpyHwnd)) {
        console.log("[WindowManager] scrcpy cerrado, deteniendo dock");
        detachFromMirror();
        return;
      }
      syncWindows(scrcpyHwnd, electronHwnd, PANEL_WIDTH);
    } catch (err) {
      console.error("[WindowManager] Error en sync periódico:", err);
      detachFromMirror();
    }
  }, 150);

  return true;
}

/**
 * Stop syncing and let the user move the Electron window freely.
 */
export function detachFromMirror(): void {
  if (syncInterval !== null) {
    clearInterval(syncInterval);
    syncInterval = null;
    console.log("[WindowManager] Dock detenido");
  }
  lastScrcpyRect = { left: 0, top: 0, right: 0, bottom: 0 };
}
