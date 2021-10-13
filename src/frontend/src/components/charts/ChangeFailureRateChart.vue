<template>
  <div class="chartAreaWrapper flex flex-col">
    <div class="chartWrapper shadow-lg">
      <apexchart
        type="line"
        height="350"
        :options="chartOptions"
        :series="changeFailureRateData"
      ></apexchart>
    </div>
    <div
      class="
        mt-4
        w-1/2
        mx-auto
        font-semibold
        text-center
        rounded-md
        py-3
        flex flex-row
        justify-apart
      "
      :class="{
        'bg-green-600 text-white': perfStatus == 'High',
        'bg-yellow-400 text-rrgrey-800': perfStatus == 'Medium',
        'bg-red-600 text-white': perfStatus == 'Low',
      }"
    >
      <div class="spacer"></div>
      <h1 class="mx-auto text-xl">
        {{ Math.round(changeFailureRate?.change_failure_rate * 100) / 100 }}
      </h1>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="mr-4 h-8 w-8 text-white inline-block hover:text-rrgrey-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        @click="showInfoModal = true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </div>
    <teleport to="#modals">
      <infoModal
        v-if="showInfoModal"
        @close="showInfoModal = false"
        :infoForStatus="infoForStatus"
        :status="perfStatus"
        :modalType="modalType"
      >
      </infoModal>
    </teleport>
  </div>
</template>

<script lang="ts">
import VueApexCharts from "vue3-apexcharts";
export default {
  components: {
    apexchart: VueApexCharts,
  },
};
</script>

<script lang="ts" setup>
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */

import { defineProps, PropType, ref, onMounted, watch, computed } from "vue";
import axios from "axios";
import { infoForStatusItem, changeFailureRateItem } from "../../types";
import infoModal from "../InfoModal.vue";

/* ----------------------------------------------
                  PROPS
---------------------------------------------- */

const props = defineProps({
  projectName: {
    type: String as PropType<string>,
    required: true,
    default: "All",
  },
  infoForStatus: {
    type: Object as PropType<infoForStatusItem>,
    required: true,
  },
});

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */

const changeFailureRate = ref<changeFailureRateItem>(); // holds currently fetched deployment data

const perfStatus = ref("0-15%");
const showInfoModal = ref(false);
const modalType = ref("changeFailureRate");
const chartOptions = ref({
  chart: {
    height: 350,
    type: "line",
  },
  dataLabels: {
    enabled: false,
  },
  xaxis: {
    type: "datetime",
  },
  yaxis: {
    forceNiceScale: true,
  },
});

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchChangeFailureRate() {
  //set url string
  let url = "";
  if (props.projectName == "All") {
    url = "metrics/ChangeFailureRate";
  } else {
    url =
      "metrics/ChangeFailureRate?&project_name=" +
      encodeURIComponent(props.projectName);
  }
  // retrieve deployments
  axios
    .get(url, {
      params: {},
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((response) => {
      changeFailureRate.value = response.data;
      if (response.data.change_failure_rate <= 0.15) {
        perfStatus.value = "High";
      } else if (response.data.change_failure_rate <= 0.45) {
        perfStatus.value = "Medium";
      } else {
        perfStatus.value = "Low";
      }
    })
    .catch((error) => {
      console.error("GET Lead Time Error: ", error);
    });
}

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

// Data used in deployments chart. Pairs of [unix timestamp, number of deployments on that day]
const changeFailureRateData = computed(() => {
  if (changeFailureRate.value) {
    return [
      {
        name: "Change Failure Rate",
        color: "#10069f",
        data: changeFailureRate.value.daily_change_failure_rate.map(
          (a: any) => [new Date(a[0] * 1000), a[1]]
        ),
      },
    ];
  } else {
    return [];
  }
});

/* ----------------------------------------------
                     WATCHERS              
  ---------------------------------------------- */

/* Watch to update data when changing selected project */
watch(
  () => props.projectName,
  (val, oldVal) => {
    fetchChangeFailureRate();
  }
);

/* ----------------------------------------------
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */

onMounted(() => {
  fetchChangeFailureRate();
});
</script>
