<template>
  <div class="chartAreaWrapper flex flex-col">
    <h1 class="text-xl font-semibold text-rrgrey-700 mb-2">Time To Restore</h1>
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
          'text-green-600': perfStatus == 'Less than one hour',
          'text-yellow-400': perfStatus == 'Less than one Day',
          'text-orange-500': perfStatus == 'Less than one week',
          'text-red-600': perfStatus == 'Between one week and one month',
          'text-rrgrey-700': perfStatus == 'No closed production defects',
        }"
      >
        {{ perfStatus }}
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
        :series="timeToRestoreData"
      ></apexchart>
    </div>
    <LoadingModal :modal-height="chartOptions.chart.height + 15" v-else />
    <div></div>
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
import { infoForStatusItem, timeToRestoreItem } from "../../types";
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

const timeToRestore = ref<timeToRestoreItem>(); // holds currently fetched deployment data

const perfStatus = ref("Less than one week");
const showInfoModal = ref(false);
const modalType = ref("timeToRestore");
const loaded = ref(false);
const last30DaysPercentage = ref(4.2);
const last30DaysValue = ref(6.5);
const last90DaysPercentage = ref(-4.5);
const last90DaysValue = ref(3.7);

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
    labels: {
      formatter: (val: number) => {
        return Math.round(val * 100) / 100;
      },
    },
  },
});

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchTimeToRestore() {
  //set url string
  let url = import.meta.env.VITE_API_URL;
  if (props.projectName == "All") {
    url = "/metrics/TimeToRestore";
  } else {
    url =
      "/metrics/TimeToRestore?&project_name=" +
      encodeURIComponent(props.projectName);
  }
  // retrieve deployments
  axios
    .get(url, {
      params: {},
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${import.meta.env.VITE_API_AUTH_TOKEN}`,
      },
    })
    .then((response) => {
      timeToRestore.value = response.data;
      // perfStatus.value = response.data.performance;
      loaded.value = true;
    })
    .catch((error) => {
      console.error("GET Time To Restore Error: ", error);
    });
}

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

// Data used in deployments chart. Pairs of [unix timestamp, number of deployments on that day]
const timeToRestoreData = computed(() => {
  if (timeToRestore.value) {
    return [
      {
        name: "Time to Restore (hours)",
        color: "#10069f",
        data: timeToRestore.value.daily_times_to_restore.map((a: any) => [
          new Date(a[0] * 1000),
          a[1],
        ]),
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
    fetchTimeToRestore();
  }
);

/* ----------------------------------------------
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */

onMounted(() => {
  fetchTimeToRestore();
});
</script>
