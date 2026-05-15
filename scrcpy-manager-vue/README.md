# Scrcpy Manager Desktop (Electron + Vue)

Aplicacion de escritorio para administrar dispositivos Android con scrcpy, construida con Electron, Vue 3 y TypeScript. El frontend consume el backend de Mobile.Remote.Toolkit.Api para listar dispositivos, iniciar/detener mirror y ejecutar acciones ADB.

## Resumen

- UI en Vue 3 + Vuetify
- App de escritorio con Electron
- Comunicacion con API REST y SignalR
- Scripts de desarrollo para levantar frontend + backend
- Pipeline de distribucion para instalador Windows

## Tecnologias

- Electron 41
- electron-vite 5
- Vue 3.5
- TypeScript 5.8
- Vuetify 3.9
- Axios
- SignalR cliente (@microsoft/signalr)

## Requisitos

- Windows 10/11
- Node.js 20+ recomendado
- pnpm 9+ recomendado
- .NET 8 SDK (para correr/publicar backend)
- Herramientas Android en Tools del backend:
  - Mobile.Remote.Toolkit.Api/Tools/Android/adb/adb.exe
  - Mobile.Remote.Toolkit.Api/Tools/Android/scrcpy/scrcpy.exe

## Instalacion

```bash
pnpm install
```

## Comandos

### Desarrollo

```bash
pnpm dev
```

Inicia solo el renderer de Vite en http://localhost:3000.

```bash
pnpm electron:dev
```

Inicia Electron en modo desarrollo (requiere backend ya levantado).

```bash
pnpm dev:full
```

Flujo completo en Windows:
1. Verifica herramientas Android.
2. Levanta el backend .NET en una ventana aparte.
3. Espera hasta que el endpoint de API responda.
4. Inicia Electron.

### Backend Helpers

```bash
pnpm backend:start
pnpm backend:check
pnpm tools:check
```

- backend:start: ejecuta el API .NET en Development.
- backend:check: verifica disponibilidad del API en https://localhost:59399/api/android/devices.
- tools:check: valida existencia de adb y scrcpy en la carpeta Tools.

### Build y Distribucion

```bash
pnpm electron:build
pnpm electron:pack
pnpm electron:dist
```

- electron:build: compila main, preload y renderer a out/.
- electron:pack: genera carpeta unpacked.
- electron:dist: genera instalador con electron-builder.

Flujo empaquetado completo del producto (incluye backend publish):

```bash
pnpm dist
pnpm dist:skip-api
pnpm dist:quick
```

## Configuracion

La URL base del backend se define en src/services/api.ts con este orden:

1. Variable de entorno VITE_API_BASE_URL.
2. Fallback a http://localhost:59399/api.

Ejemplo .env local:

```env
VITE_API_BASE_URL=http://localhost:59400/api
```

## Estructura principal

```text
electron/
  main/            # Proceso principal de Electron
  preload/         # Bridge seguro IPC
src/
  components/      # Componentes UI
  composables/     # Logica reutilizable
  services/        # Cliente API y SignalR
  stores/          # Estado de aplicacion
scripts/
  dev.ps1          # Orquestacion desarrollo completo
  build-dist.ps1   # Publish backend + build + instalador
```

## Endpoints usados por la app

- GET /api/android/devices
- POST /api/android/devices/{serial}/mirror/start
- POST /api/android/devices/{serial}/mirror/stop
- POST /api/android/devices/{serial}/screenshot
- POST /api/android/devices/{serial}/action
- POST /api/android/devices/{serial}/adb
- GET /api/android/devices/{serial}/status
- GET /api/monitoring/status
- POST /api/monitoring/start
- POST /api/monitoring/stop

## Solucion de problemas

- Si Electron abre pero no lista dispositivos, ejecutar pnpm backend:check.
- Si falla mirror o acciones ADB, ejecutar pnpm tools:check.
- Si hay error SSL en desarrollo, validar que el backend este en https://localhost:59399.

## Proyecto relacionado

Este cliente depende del backend en la carpeta Mobile.Remote.Toolkit.Api del workspace.
