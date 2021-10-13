<template>
  <div
    class="flex justify-center items-center"
    :style="`height: ${modalHeight}px; width: ${modalWidth}px`"
  >
    <!-- <div style="`height: ${modalHeight}px`"> -->
    <img src="../assets/img/loader.png" alt="Loading" />
  </div>
</template>

<script setup lang="ts">
// To use this loader modal, you will need to create a "loaded" variable and set it to false. Then, when you do an API call and the data has finished loading, set the variable back to true.
import { defineProps, PropType } from "vue";

const props = defineProps({
  modalWidth: {
    type: Number as PropType<number>,
    required: false,
  },
  modalHeight: {
    type: Number as PropType<number>,
    required: false,
  },
});
</script>
