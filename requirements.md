# Requerimientos del Proyecto Scrcpy Manager

Este proyecto utiliza una arquitectura **backend en Python** y **frontend en Vue**.  
A continuación se detallan los principales paquetes y herramientas necesarias para cada entorno.

---

## Backend (Python)

**Framework principal:** Flask  
**Validación de datos:** Pydantic  
**Procesos y monitoreo:** psutil  
**CORS:** flask-cors

### Requerimientos principales

| Paquete    | Descripción                                         |
| ---------- | --------------------------------------------------- |
| flask      | Microframework para construir APIs REST.            |
| flask-cors | Permite solicitudes entre dominios (CORS) en Flask. |
| pydantic   | Modelos y validación de datos para los schemas.     |
| psutil     | Utilidades para monitorear y gestionar procesos.    |

#### Instalación

```bash
pip install flask flask-cors pydantic psutil
```

#### Archivo `requirements.txt`

```
flask
flask-cors
pydantic
psutil
```

---

## Frontend (Vue)

**Framework principal:** Vue
**Gestión de rutas:** vue-router
**HTTP requests:** axios

### Requerimientos principales

| Paquete    | Descripción                                         |
| ---------- | --------------------------------------------------- |
| vue        | Framework progresivo para construir interfaces web. |
| vue-router | Gestión de rutas en aplicaciones SPA.               |
| vuex       | Gestión de estado centralizado (opcional).          |
| axios      | Cliente HTTP para consumir la API Flask.            |

#### Instalación

```bash
npm install vue vue-router axios
```

#### Archivo `package.json` (fragmento relevante)

```json
"dependencies": {
  "vue": "^3.0.0",
  "vue-router": "^4.0.0",
  "axios": "^1.0.0",
  "vuex": "^4.0.0"
}
```

---

## Otros requerimientos y recomendaciones

- **Python 3.8+** recomendado.
- **Node.js 14+** para el entorno Vue.
- **scrcpy** debe estar instalado en el sistema para el manejo de dispositivos Android.
- Configura variables de entorno si tu API requiere rutas personalizadas o credenciales.

---

## Notas

- Para desarrollo local, asegúrate de tener ambos entornos configurados y ejecutando:
  - Backend: `python server.py`
  - Frontend: `pnpm run serve` (o el comando equivalente de Vue)
