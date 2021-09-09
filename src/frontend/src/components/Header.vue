<template>
  <div class="wrapper">
    <nav
      class="
        font-sans
        flex flex-row
        justify-start
        text-center
        sm:flex-row sm:text-left sm:justify-start
        bg-rrblue-800
        w-h
        h-16
        leading-16
      "
    >
      <div class="mr-2 ml-6">
        <a href="/"
          ><img class="w-8 mt-3" src="../assets/img/monogram.jpg"
        /></a>
      </div>
      <div class="h-16">
        <router-link class="" :to="{ name: 'Home' }"
          ><div
            class="
              text-xl
              leading-16
              no-underline
              text-white
              hover:text-white
              mr-6
              font-sans
            "
          >
            <span class="text-rrpink-400" v-if="env == 'development'">dev</span
            >Metrics
          </div></router-link
        >
      </div>
    </nav>
  </div>
</template>

<script>
import { ref, defineComponent } from "vue";

export default defineComponent({
  name: "Header",
  components: {},
  setup() {
    const env = process.env.VUE_APP_ENV;

    return {
      env,
    };
  },
});
</script>

<style scoped>
.userDropDownFade-enter-active,
.userDropDownFade-leave-active {
  transition: all 0.1s ease-in-out;
}

.userDropDownFade-enter-from,
.userDropDownFade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
