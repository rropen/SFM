import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./index.css"; // for tailwindCSS
import { createPinia } from "pinia";
import VueApexCharts from "vue3-apexcharts";

import PrimeVue from "primevue/config";
import axios from "axios";

axios.defaults.baseURL = "http://localhost:8181";

createApp(App)
  .use(router)
  .use(PrimeVue)
  .use(createPinia())
  .use(VueApexCharts)
  .mount("#app");
