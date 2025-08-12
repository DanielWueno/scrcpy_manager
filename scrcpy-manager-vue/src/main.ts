import { createApp } from "vue";
import App from "./App.vue";
import { createVuetify } from "vuetify";
import "@mdi/font/css/materialdesignicons.css";
import "./styles/global.css";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import "vuetify/lib/styles/main.sass";

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "light",
    themes: {
      dark: {
        colors: {
          primary: "#546E7A", // Azul gris
          secondary: "#37474F", // Gris azulado oscuro
          accent: "#607D8B", // Azul gris suave
          success: "#4CAF50", // Verde éxito (mantenido)
          warning: "#FFA726", // Naranja suave
          error: "#EF5350", // Rojo suave
          info: "#42A5F5", // Azul información suave
          background: "#263238", // Gris azulado oscuro
          surface: "#37474F", // Superficie gris
        },
      },
      light: {
        colors: {
          primary: "#546E7A", // Azul gris
          secondary: "#37474F", // Gris azulado
          accent: "#607D8B", // Azul gris suave
          success: "#4CAF50", // Verde éxito
          warning: "#e5ff00ff", // Naranja suave
          error: "#EF5350", // Rojo suave
          info: "#42A5F5", // Azul información suave
          background: "#FAFAFA", // Fondo muy claro
          surface: "#FFFFFF", // Superficie blanca
        },
      },
    },
  },
});

createApp(App).use(vuetify).mount("#app");
