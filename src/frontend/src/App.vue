<template>
  <div class="bg-rrblue-800 min-h-full overflow-auto">
    <div id="app" class="h-full font-sans bg-rrgrey-200" style="top: 50%">
      <Header />
      <div class="flex flex-col">
        <div id="sidebarWrapper"></div>
      </div>
      <div class="page bg-rrgrey-200 h-full">
        <router-view />
      </div>
      <Footer />
    </div>
  </div>
</template>

<script lang="ts" setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import { defineComponent, computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const pathName = computed(() => route.name);
</script>
<style></style>
