import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/dora",
    name: "DORA",
    component: () => import("../views/DORA.vue"),
  },
  {
    path: "/flow",
    name: "Flow",
    component: () => import("../views/Flow.vue"),
  },
  {
    path: "/about",
    name: "About",
    component: () => import("../views/About.vue"),
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("../views/Admin.vue"),
  },
  {
    path: "/422",
    name: "422",
    component: () => import("../views/422.vue"),
  },
  {
    path: "/401",
    name: "401",
    component: () => import("../views/401.vue"),
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("../views/404.vue"),
  },
];

const router = createRouter({
  // history: createWebHistory(process.env.BASE_URL),
  history: createWebHistory("/"),
  routes,
});

export default router;
