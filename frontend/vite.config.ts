import { resolve } from "path";
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    rollupOptions: {
      input: {
        index: resolve(__dirname, "index/index.html"),
        login: resolve(__dirname, "login/index.html"),
        admin: resolve(__dirname, "admin/index.html"),
      },
    },
  },
});
