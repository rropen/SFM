<template>
  <apexchart
    ref="realtimeChart"
    type="line"
    height="350"
    :options="chartOptions"
    :series="series"
  ></apexchart>
</template>
<script lang="ts" setup>
import VueApexCharts from "vue3-apexcharts";
import { defineProps, PropType } from "vue";

const props = defineProps({
  projectName: {
    type: String as PropType<string>,
    required: true,
    default: "All",
  },
});
</script>
