<template>
  <div
    @keyup.esc="onClose"
    ref="infoModal"
    class="
      modalbg
      flex
      items-center
      justify-center
      fixed
      bg-opacity-90
      left-0
      bottom-0
      w-full
      h-full
      bg-rrgrey-800
      py-12
    "
    tabindex="0"
  >
    <div
      class="
        modalBox
        bg-white
        rounded-lg
        w-1/2
        xl:w-1/4
        px-4
        py-4
        flex flex-col
        items-center
        overflow-auto
      "
    >
      <div class="mx-auto h-full w-10/12">
        <div class="icon text-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="mr-4 h-20 w-20 text-rrblue-600 inline-block"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <header class="text-rrgrey-900 font-medium text-2xl mb-2 mt-12">
          <h3 class="text-center text-2xl">
            {{ status }}
          </h3>
          <p
            v-html="infoForStatus[`${modalType}`][`${status}`].info"
            class="text-rrgrey-600 text-lg font-base mt-4"
          ></p>
        </header>
        <main class="text-rrgrey-800 text-lg flex justify-center mt-12">
          <rrButton
            :primary="false"
            size="medium"
            label="Close"
            @click="onClose"
          />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { rrButton } from "@rrglobal/vue-cobalt";
import { infoForStatusItem } from "../types";
import { PropType, onMounted, ref, computed } from "vue";

const props = defineProps({
  status: {
    type: String as PropType<String>,
    required: true,
  },
  infoForStatus: {
    type: Object as PropType<infoForStatusItem>,
    required: true,
  },
  modalType: {
    type: String as PropType<string>,
    required: true,
    default: "Deployments",
  },
});

const emits = defineEmits(["close"]);
const infoModal = ref<null | { focus: () => null }>();

// Close button is clicked
const onClose = () => {
  emits("close");
};

onMounted(() => {
  infoModal.value?.focus();
});
</script>
