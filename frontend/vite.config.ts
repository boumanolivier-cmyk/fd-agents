import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Detect if running in Docker by checking for Docker-specific env var
// or use the VITE_BACKEND_URL environment variable
const isDocker = process.env.DOCKER_ENV === "true";
const backendUrl =
  process.env.VITE_BACKEND_URL ||
  (isDocker ? "http://backend:8000" : "http://localhost:8000");

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Listen on all addresses when in Docker
    proxy: {
      "/api": {
        target: backendUrl,
        changeOrigin: true,
      },
      "/charts": {
        target: backendUrl,
        changeOrigin: true,
      },
    },
  },
});
