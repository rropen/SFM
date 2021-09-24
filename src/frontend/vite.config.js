import vue from "@vitejs/plugin-vue";
import istanbul from "vite-plugin-istanbul";

export default {
  plugins: [
    vue(),
    istanbul({
      include: "src/*",
      exclude: ["node_modules", "test/"],
      extension: [".js", ".ts", ".vue"],
      cypress: true,
    }),
  ],
  define: {
    "process.env": {},
  },
};
