# SCRCPY Manager

**Gestor profesional de dispositivos Android con interfaz web moderna y API modular**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-green.svg)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red.svg)](https://flask.palletsprojects.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://typescriptlang.org)

## Descripción

SCRCPY Manager es una aplicación completa para gestionar dispositivos Android remotamente. Combina la potencia de **scrcpy** con una interfaz web moderna y una API RESTful modular para control profesional de dispositivos.

### Características Principales

- **Interfaz Web Moderna**: Vue.js 3 + Vuetify con diseño profesional
- **Conexión Flexible**: USB y WiFi (TCP/IP)
- **Capturas de Pantalla**: Con descarga automática
- **Control Remoto**: Pantalla, mirror, controles básicos
- **Refresh Inteligente**: Sistema adaptativo para optimizar recursos
- 🏗️ **API Modular**: Arquitectura profesional con servicios separados
- 📱 **Multi-dispositivo**: Gestión simultánea de múltiples dispositivos

## 🚀 Instalación Rápida

### Prerrequisitos

1. **Python 3.8+** instalado
2. **Node.js 16+** y **pnpm** instalado
3. **ADB (Android Debug Bridge)** en PATH
4. **scrcpy** instalado y accesible

```bash
# Verificar prerrequisitos
python --version
node --version
pnpm --version
adb version
scrcpy --version
```

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/dankewolfy/scrcpy_manager.git
cd scrcpy_manager

# 2. Instalar dependencias Python
pip install flask flask-cors pydantic

# 3. Instalar dependencias del frontend
cd scrcpy-manager-vue
pnpm install

# 4. Construir el frontend
pnpm build
```

## Uso

### Iniciar la Aplicación

```bash
# Opción 1: API Modular (Recomendado)
cd api
python main.py

# Opción 2: Servidor tradicional
python api/server.py

# Opción 3: Frontend en desarrollo
cd scrcpy-manager-vue
pnpm dev
```

### Acceso Web

- **Frontend**: http://localhost:5173 (desarrollo) o http://localhost:5000 (producción)
- **API**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health

### Conectar Dispositivos

#### USB (Recomendado)

1. Conectar dispositivo por USB
2. Habilitar **Depuración USB** en el dispositivo
3. Aceptar la conexión en el dispositivo
4. El dispositivo aparecerá automáticamente

#### WiFi/TCP

1. Conectar dispositivo por USB primero
2. Ejecutar: `adb tcpip 5555`
3. Desconectar USB
4. Usar la IP del dispositivo para conectar

## API Reference

### Endpoints Principales

#### Dispositivos

```http
GET    /api/devices              # Listar dispositivos
POST   /api/devices/connect      # Conectar dispositivo
DELETE /api/devices/{id}         # Desconectar dispositivo
GET    /api/devices/{id}/info    # Info del dispositivo
```

#### Capturas

```http
POST   /api/screenshots/{device_id}    # Tomar screenshot
GET    /api/screenshots               # Listar screenshots
GET    /api/screenshots/download/{filename}  # Descargar screenshot
```

#### Acciones

```http
POST   /api/actions/{device_id}/screen_on    # Encender pantalla
POST   /api/actions/{device_id}/screen_off   # Apagar pantalla
POST   /api/actions/{device_id}/mirror_on    # Activar mirror
POST   /api/actions/{device_id}/mirror_off   # Desactivar mirror
POST   /api/actions/{device_id}/home         # Botón Home
POST   /api/actions/{device_id}/back         # Botón Atrás
POST   /api/actions/{device_id}/recent       # Apps recientes
```

### Ejemplos de Uso

#### Tomar Screenshot

```bash
curl -X POST http://localhost:5000/api/screenshots/DEVICE_ID \
  -H "Content-Type: application/json" \
  -d '{"download": true}'
```

#### Conectar por TCP

```bash
curl -X POST http://localhost:5000/api/devices/connect \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.1.100", "port": 5555}'
```

#### Control de Pantalla

```bash
# Apagar pantalla del dispositivo
curl -X POST http://localhost:5000/api/actions/DEVICE_ID/screen_off

# Activar mirror
curl -X POST http://localhost:5000/api/actions/DEVICE_ID/mirror_on
```

## Arquitectura

### Estructura del Proyecto

```
scrcpy_manager/
├── api/                        # API Backend Modular
│   ├── config/                 # Configuración centralizada
│   ├── schemas/                # Validación Pydantic
│   ├── services/               # Lógica de negocio
│   ├── routers/                # Endpoints organizados
│   ├── middleware/             # CORS, Errors, Logging
│   ├── utils/                  # Utilidades reutilizables
│   └── main.py                 # Punto de entrada
├── scrcpy-manager-vue/         # Frontend Vue.js
│   ├── src/components/         # Componentes UI
│   ├── src/composables/        # Lógica reutilizable
│   ├── src/services/           # Servicios API
│   └── src/types/              # Definiciones TypeScript
├── core/                       # Módulos Python core
│   ├── device_manager.py       # Gestión de dispositivos
│   └── scrcpy_controller.py    # Control de scrcpy
└── gui/                        # Interfaz GUI (Tkinter)
```

### Tecnologías Utilizadas

#### Backend

- **Flask**: Framework web ligero
- **Pydantic**: Validación de datos
- **Asyncio**: Operaciones asíncronas
- **Subprocess**: Integración con scrcpy/adb

#### Frontend

- **Vue.js 3**: Framework reactivo
- **Vuetify**: Librería de componentes Material Design
- **TypeScript**: Tipado estático
- **Vite**: Build tool

## Configuración

### Variables de Entorno

```bash
# .env (opcional)
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=false
SECRET_KEY=tu-clave-secreta
SCREENSHOT_DIR=./screenshots
LOG_LEVEL=INFO
```

### Configuración Avanzada

#### Personalizar Puertos

```python
# api/config/settings.py
API_HOST = "localhost"
API_PORT = 8080
```

#### Configurar Logging

```python
# api/config/logging.py
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

#### CORS Personalizado

```python
# api/middleware/cors.py
CORS_ORIGINS = ["http://localhost:3000", "http://tu-dominio.com"]
```

## Características de UI

### Funcionalidades de UI

- **Lista de Dispositivos**: Vista en tiempo real con estado
- **Refresh Inteligente**: Se adapta según visibilidad y actividad
- **Capturas**: Descarga automática al navegador
- **Controles**: Botones para todas las acciones principales
- **Estados**: Loading, error y success con feedback

## Consideraciones de Seguridad

### Conexiones USB

- **Seguro**: Conexión directa sin exposición de red
- **Confiable**: No requiere configuración adicional
- **Rápido**: Latencia mínima

### Conexiones TCP/IP

- **Red Local**: Solo usar en redes confiables
- **Firewall**: El dispositivo debe permitir conexiones en puerto 5555
- **Exposición**: Puerto abierto mientras esté activo

### Recomendaciones

1. **Usar USB** siempre que sea posible
2. **Cerrar conexiones TCP** cuando no se usen
3. **Red privada** para conexiones WiFi
4. **Autenticación** adicional para producción

## Troubleshooting

### Problemas Comunes

#### Dispositivo no aparece

```bash
# Verificar conexión ADB
adb devices

# Reiniciar servidor ADB
adb kill-server
adb start-server

# Verificar permisos
adb shell
```

#### Error de conexión TCP

```bash
# Verificar puerto
adb tcpip 5555

# Verificar conectividad
ping IP_DISPOSITIVO
telnet IP_DISPOSITIVO 5555
```

#### scrcpy no inicia

```bash
# Verificar instalación
scrcpy --version

# Probar conexión manual
scrcpy -s DEVICE_ID

# Verificar dependencias
scrcpy --help
```

#### API no responde

```bash
# Verificar puerto
netstat -an | findstr :5000

# Logs de la aplicación
python api/main.py

# Verificar health check
curl http://localhost:5000/api/health
```

### Logs y Debug

#### Activar Debug Mode

```python
# api/config/settings.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

#### Ver Logs en Tiempo Real

```bash
# Backend logs
tail -f logs/app.log

# Frontend logs (navegador)
F12 -> Console -> Ver errores
```

## Deployment

### Desarrollo Local

```bash
# Backend
cd api && python main.py

# Frontend
cd scrcpy-manager-vue && pnpm dev
```

### Producción

```bash
# Construir frontend
cd scrcpy-manager-vue
pnpm build

# Servir con Flask
cd api
python main.py
```

### Docker

```dockerfile
# Dockerfile ejemplo
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "api/main.py"]
```

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Autor

**dankewolfy (El Wueno)** - _Desarrollo completo :'D_

## Agradecimientos

- **scrcpy team** - Por la excelente herramienta de mirroring
- **Vue.js community** - Por el framework increíble
- **Flask community** - Por el microframework flexible
- **Material Design** - Por las guías de diseño

---

**¡Disfruta gestionando tus dispositivos Android de manera INNOVADORA!**
