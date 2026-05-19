import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "web-build"
  },
  resolve: {
    alias: {
      "plotly.js-dist-min": path.resolve(rootDir, "node_modules/plotly.js-dist-min/plotly.min.js"),
      "papaparse": path.resolve(rootDir, "node_modules/papaparse/papaparse.js"),
      "@/lib": path.resolve(rootDir, "app-lib"),
      "@": rootDir
    }
  },
  server: {
    port: 3010,
    strictPort: true,
    fs: {
      allow: [rootDir, path.resolve(rootDir, "..")]
    }
  },
  preview: {
    port: 3010,
    strictPort: true
  }
});
