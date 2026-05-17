import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "build"
  },
  resolve: {
    alias: {
      "@": "/src"
    }
  },
  server: {
    port: 3010,
    strictPort: true
  },
  preview: {
    port: 3010,
    strictPort: true
  }
});
