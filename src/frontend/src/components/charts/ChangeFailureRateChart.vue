<template>
  <div class="chartAreaWrapper flex flex-col">
    <h1 class="text-xl font-semibold text-rrgrey-700 mb-2">
      Change Failure Rate
    </h1>
    <div class="flex">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="mr-2 h-6 w-6 text-rrgrey-700 hover:text-rrgrey-600"
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
      <h1
        :class="{
          'text-green-600': perfStatus == 'High',
          'text-yellow-400': perfStatus == 'Medium',
          'text-red-600': perfStatus == 'Low',
        }"
      >
        {{ perfStatus }} ({{
          Math.round(changeFailureRate?.change_failure_rate * 100)
        }}%)
      </h1>
      <h1 class="ml-4 mr-1 text-rrgrey-700">
        Last 30 Days: {{ last30DaysValue }}
      </h1>
      <h1
        :class="{
          'text-green-600': last30DaysPercentage >= 0,
          'text-red-600': last30DaysPercentage < 0,
        }"
      >
        ({{ last30DaysPercentage }}%)
      </h1>

      <h1 class="ml-4 mr-1 text-rrgrey-700">
        Last 90 Days: {{ last90DaysValue }}
      </h1>
      <h1
        :class="{
          'text-green-600': last90DaysPercentage >= 0,
          'text-red-600': last90DaysPercentage < 0,
        }"
      >
        ({{ last90DaysPercentage }}%)
      </h1>
    </div>
    <div v-if="loaded" class="chartWrapper">
      <apexchart
        type="line"
        :height="chartOptions.chart.height"
        :options="chartOptions"
        :series="changeFailureRateData"
      ></apexchart>
    </div>
    <LoadingModal :modal-height="chartOptions.chart.height + 15" v-else />

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
import LoadingModal from "../LoadingModal.vue";

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
let base = import.meta.env.VITE_API_URL;
const changeFailureRate = ref<changeFailureRateItem>(); // holds currently fetched deployment data

const perfStatus = ref("0-15%");
const showInfoModal = ref(false);
const modalType = ref("changeFailureRate");
const loaded = ref(false);
const last30DaysPercentage = ref(2.2);
const last30DaysValue = ref(5.5);
const last90DaysPercentage = ref(-8.5);
const last90DaysValue = ref(8.7);

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
  let bearer = import.meta.env.VITE_API_AUTH_TOKEN;
  //set url string
  // let url = import.meta.env.VITE_API_URL;
  let url = "";
  if (props.projectName == "All") {
    url = "/metrics/ChangeFailureRate";
  } else {
    url =
      "/metrics/ChangeFailureRate?&project_name=" +
      encodeURIComponent(props.projectName);
  }
  // retrieve deployments
  axios
    .get(url, {
      params: {},
      headers: {
        "Content-Type": "application/json",
        // Authorization: `Bearer ${import.meta.env.VITE_API_AUTH_TOKEN}`,
        Authorization: "Bearer " + bearer,
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
      loaded.value = true;
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
    loaded.value = false;
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
