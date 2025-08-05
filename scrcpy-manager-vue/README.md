# Vue 3 + TypeScript + Vite

# Scrcpy Manager Vue

Una interfaz web moderna y elegante para gestionar dispositivos Android usando Scrcpy, construida con Vue 3, TypeScript y Vuetify.

## 🚀 Características

- **Interfaz moderna**: Diseño Material Design con Vuetify 3
- **TypeScript**: Desarrollo type-safe y mantenible
- **Gestión de dispositivos**: Detección automática y conexión de dispositivos Android
- **Controles remotos**: Screenshots, grabación, controles de pantalla
- **Configuración rápida**: Opciones predefinidas para conexiones scrcpy
- **Notificaciones en tiempo real**: Sistema de toast notifications
- **Auto-refresh**: Actualización automática del estado de dispositivos
- **Responsive**: Diseño adaptativo para diferentes tamaños de pantalla

## 🛠️ Stack Tecnológico

- **Vue 3.5** - Framework progresivo de JavaScript
- **TypeScript 5.8** - JavaScript con tipado estático
- **Vuetify 3.9** - Framework de componentes Material Design
- **Vite 7** - Build tool rápido y moderno
- **Axios** - Cliente HTTP para comunicación con API
- **Material Design Icons** - Iconografía consistente

## 📁 Estructura del Proyecto

```
src/
├── components/           # Componentes Vue reutilizables
│   ├── DeviceList.vue   # Lista de dispositivos conectados
│   ├── DeviceInfo.vue   # Información detallada del dispositivo
│   ├── QuickConfig.vue  # Configuración rápida de opciones
│   └── ToolbarFrame.vue # Herramientas y controles
├── composables/         # Lógica de negocio reutilizable
│   └── useDeviceManager.ts # Gestión de estado de dispositivos
├── services/           # Servicios de comunicación
│   └── api.ts         # Cliente API para backend
├── types/             # Definiciones de tipos TypeScript
│   └── index.ts      # Interfaces y tipos principales
└── views/            # Vistas/páginas (futuras expansiones)
```

## 🚦 Comandos Disponibles

```bash
# Instalar dependencias
pnpm install

# Desarrollo
npm run dev          # Servidor de desarrollo en http://localhost:3000

# Construcción
npm run build        # Build para producción
npm run preview      # Vista previa del build

# Verificación
npm run type-check   # Verificación de tipos TypeScript
npm run lint         # Análisis de código
```

## 🔧 Configuración

### Prerequisitos

- Node.js 18+
- pnpm (recomendado) o npm
- Backend API corriendo en `http://127.0.0.1:5000`

### Variables de Entorno

El proyecto usa la URL del API hardcodeada. Para cambiarla, modifica `src/services/api.ts`:

```typescript
const API_BASE_URL = "http://127.0.0.1:5000/api";
```

### Instalación y Ejecución

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd scrcpy-manager-vue
```

2. **Instalar dependencias**

```bash
pnpm install
```

3. **Ejecutar en desarrollo**

```bash
npm run dev
```

4. **Abrir en el navegador**
   - Visita http://localhost:3000

## 🏗️ API Backend

El frontend se comunica con un backend que debe exponer los siguientes endpoints:

```typescript
GET    /api/devices              # Obtener lista de dispositivos
POST   /api/devices/refresh      # Actualizar lista de dispositivos
POST   /api/devices/:serial/connect    # Conectar dispositivo
POST   /api/devices/:serial/disconnect # Desconectar dispositivo
POST   /api/devices/:serial/screenshot # Tomar captura de pantalla
POST   /api/devices/:serial/action     # Ejecutar acción en dispositivo
GET    /api/devices/:serial/status     # Obtener estado del dispositivo
```

## 🎨 Personalización

### Temas y Colores

El proyecto usa Vuetify 3 con temas personalizables. Para modificar colores y temas, edita el archivo `src/main.ts`:

```typescript
const vuetify = createVuetify({
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#1976D2",
          secondary: "#424242",
          // ... más colores
        },
      },
    },
  },
});
```

### Configuración de Vite

El proyecto incluye configuración optimizada en `vite.config.ts`:

- Alias `@` para imports
- Servidor en puerto 3000
- Chunks de vendor optimizados
- Source maps para debugging

## 🧪 Testing

Actualmente el proyecto no incluye tests, pero está preparado para:

- **Unit Tests**: Vue Test Utils + Vitest
- **E2E Tests**: Playwright o Cypress
- **Type Checking**: TypeScript compiler

## 📦 Build y Deployment

```bash
# Build para producción
npm run build

# Los archivos se generan en dist/
# Sirve los archivos estáticos desde cualquier servidor web
```

El build genera:

- Archivos HTML, CSS y JS optimizados
- Source maps para debugging
- Assets con hash para cache busting
- Chunks separados para carga optimizada

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

### Estándares de Código

- **TypeScript**: Uso obligatorio para type safety
- **ESLint**: Configuración estricta para calidad de código
- **Prettier**: Formateo automático consistente
- **Vue 3 Composition API**: Patrón preferido para componentes

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🔗 Enlaces Útiles

- [Vue 3 Documentation](https://vuejs.org/)
- [Vuetify 3 Documentation](https://vuetifyjs.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Scrcpy Repository](https://github.com/Genymobile/scrcpy)

## 🐛 Problemas Conocidos

- Requiere backend API funcionando para operaciones completas
- Las notificaciones toast son temporales (no persistentes)
- Auto-refresh puede impactar performance con muchos dispositivos

## 🔄 Roadmap

- [ ] Tests unitarios y E2E
- [ ] Internacionalización (i18n)
- [ ] Configuración persistente del usuario
- [ ] Modo offline/fallback
- [ ] Metricas y analytics
- [ ] PWA capabilities

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).
