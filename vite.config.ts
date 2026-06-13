import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    setupFiles: ["./web/test-setup.ts"],
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
  },
  build: {
    target: "es2022",
    sourcemap: false,
  },
});
