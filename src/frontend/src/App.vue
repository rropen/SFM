<template>
  <div class="bg-rrblue-800 min-h-full overflow-auto">
    <div id="app" class="h-full font-sans bg-rrgrey-200" style="top: 50%">
      <Header />
      <div class="page bg-rrgrey-200 h-full">
        <router-view />
      </div>
      <rrFooter appTitle="SFM" :appText="appText" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import { rrFooter } from "@rrglobal/vue-cobalt";
import { defineComponent, computed } from "vue";
import { useRoute } from "vue-router";

const appText =
  "SFM (Software Factory Metrics) is an app to present DevOps metrics for the various applications being built throughout the Software Factory.  These include metrics such as Deployment Frequency which can give insights into the health of the software delivery processes at work and business value delivery in the greater Software Value Stream.";
const route = useRoute();
const pathName = computed(() => route.name);
console.log("VITE_API_URL", import.meta.env.VITE_API_URL);
</script>
<style></style>
