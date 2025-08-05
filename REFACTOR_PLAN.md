# Scrcpy Manager API - Estructura Modular

## Estructura Propuesta:

```
api/
├── __init__.py
├── main.py                 # Punto de entrada principal
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuraciones centralizadas
│   └── logging.py          # Configuración de logging
├── routers/
│   ├── __init__.py
│   ├── devices.py          # Endpoints de dispositivos
│   ├── screenshots.py      # Endpoints de capturas
│   └── actions.py          # Endpoints de acciones
├── services/
│   ├── __init__.py
│   ├── device_service.py   # Lógica de negocio de dispositivos
│   ├── screenshot_service.py # Lógica de capturas
│   └── action_service.py   # Lógica de acciones
├── schemas/
│   ├── __init__.py
│   ├── device.py           # Esquemas de validación
│   ├── screenshot.py       # Esquemas de capturas
│   └── action.py          # Esquemas de acciones
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py    # Manejo centralizado de errores
│   ├── cors.py            # Configuración CORS
│   └── logging.py         # Middleware de logging
└── utils/
    ├── __init__.py
    ├── response.py         # Utilidades de respuesta
    └── validators.py       # Validadores personalizados
```
