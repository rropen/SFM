import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default {
  plugins: [vue()],
  define: {
    "process.env": {},
  },
};
