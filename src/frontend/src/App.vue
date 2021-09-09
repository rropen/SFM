<template>
  <div class="bg-rrblue-800 min-h-full overflow-auto">
    <div id="app" class="h-full font-sans bg-rrgrey-200" style="top: 50%">
      <Header />
      <div class="page my-8 bg-white rounded-md h-full p-4 w-3/4 mx-auto">
        <router-view />
      </div>
      <Footer />
    </div>
  </div>
</template>
<script lang="ts">
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import { defineComponent, computed } from "vue";
import { useRoute } from "vue-router";

export default defineComponent({
  name: "App",
  components: {
    Header,
    Footer,
  },
  setup() {
    const route = useRoute();
    const pathName = computed(() => route.name);
    return { pathName };
  },
});
</script>
<style></style>
