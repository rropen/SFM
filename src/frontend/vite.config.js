import vue from "@vitejs/plugin-vue";
import istanbul from "vite-plugin-istanbul";

export default {
  plugins: [
    vue(),
    istanbul({
      include: "src/*",
      exclude: ["node_modules", "test/"],
      extension: [".js", ".ts", ".vue"],
      requireEnv: false,
    }),
  ],
  define: {
    "process.env": {},
  },
};
