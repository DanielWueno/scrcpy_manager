import { createApp } from "vue";
import App from "./App.vue";
import { createVuetify } from "vuetify";
import "@mdi/font/css/materialdesignicons.css";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import "vuetify/lib/styles/main.sass";
// Debe cargar despues de Vuetify: Vuetify no usa @layer, asi que el orden
// de import decide la cascada y global.css necesita ganarle a sus estilos.
import "./styles/global.css";

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "light",
    themes: {
      // Paleta "Liquid Glass": mismos acentos de marca en ambos temas,
      // solo cambia la superficie de vidrio sobre la que flotan.
      dark: {
        dark: true,
        colors: {
          primary: "#0381FF", // cyan de marca
          secondary: "#1920F7", // core/indigo de marca
          accent: "#8B5CF6", // purple
          success: "#34D399", // green
          warning: "#FACC15", // yellow
          error: "#F97316", // orange
          info: "#0381FF", // cyan
          purple: "#8B5CF6",
          orange: "#F97316",
          background: "#04060D",
          surface: "#0A0F1E",
        },
      },
      light: {
        dark: false,
        colors: {
          primary: "#0381FF",
          secondary: "#1920F7",
          accent: "#8B5CF6",
          success: "#34D399",
          warning: "#FACC15",
          error: "#F97316",
          info: "#0381FF",
          purple: "#8B5CF6",
          orange: "#F97316",
          background: "#EEF1FB",
          surface: "#FFFFFF",
        },
      },
    },
  },
});

createApp(App).use(vuetify).mount("#app");
