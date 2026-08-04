import { defineConfig, externalizeDepsPlugin } from "electron-vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig({
  // ── Main process ──────────────────────────────────────────────────────────
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: "out/main",
      lib: {
        entry: resolve(__dirname, "electron/main/index.ts"),
      },
    },
  },

  // ── Preload script ────────────────────────────────────────────────────────
  // Forzado a CJS: con "type": "module" en package.json, electron-vite emite el
  // preload como .mjs por default - Electron no lo cargaba como modulo ("Cannot
  // use import statement outside a module"), dejando contextBridge sin exponer
  // nada (mirrorApi/dockApi/clipboardApi undefined en el renderer). CJS + nombre
  // fijo evita la ambiguedad de resolucion de modulos de Node con "type": "module".
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      outDir: "out/preload",
      lib: {
        entry: resolve(__dirname, "electron/preload/index.ts"),
      },
      rollupOptions: {
        output: {
          format: "cjs",
          entryFileNames: "[name].js",
        },
      },
    },
  },

  // ── Renderer (Vue app) ────────────────────────────────────────────────────
  renderer: {
    root: ".",
    build: {
      outDir: "out/renderer",
      rollupOptions: {
        input: resolve(__dirname, "index.html"),
        output: {
          manualChunks: {
            vendor: ["vue", "axios"],
            vuetify: ["vuetify"],
          },
        },
      },
    },
    plugins: [vue()],
    resolve: {
      alias: {
        "@": resolve(__dirname, "src"),
      },
    },
    server: {
      port: 3000,
    },
  },
});
