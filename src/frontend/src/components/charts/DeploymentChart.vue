<template>
  <div class="chartAreaWrapper flex flex-col">
    <h1 class="text-xl font-semibold text-rrgrey-700 mb-2">Deployments</h1>
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
          'text-green-600': deploymentMetricStatus == 'Daily',
          'text-yellow-400': deploymentMetricStatus == 'Weekly',
          'text-orange-500': deploymentMetricStatus == 'Monthly',
          'text-red-600': deploymentMetricStatus == 'Yearly',
          'text-rrgrey-700': deploymentMetricStatus == 'No Deployments',
        }"
      >
        {{ deploymentMetricStatus }}
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
        type="bar"
        :height="chartOptions.chart.height"
        :options="chartOptions"
        :series="deploymentsData"
      ></apexchart>
    </div>
    <LoadingModal :modal-height="chartOptions.chart.height + 15" v-else />

    <teleport to="#modals">
      <infoModal
        v-if="showInfoModal"
        @close="showInfoModal = false"
        :infoForStatus="infoForStatus"
        :status="deploymentMetricStatus"
        :modalType="modalType"
      >
      </infoModal>
    </teleport>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
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
import { deploymentItem, infoForStatusItem } from "../../types";
import infoModal from "../InfoModal.vue";
import LoadingModal from "../LoadingModal.vue";
// import.meta.env.MODE

/* ----------------------------------------------
                  PROPS
---------------------------------------------- */

const props = defineProps({
  projectName: {
    type: String as PropType<string>,
    required: true,
  },
  infoForStatus: {
    type: Object as PropType<infoForStatusItem>,
    required: true,
  },
});

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */

const deployments = ref<deploymentItem>(); // holds currently fetched deployment data
const modalType = ref("deployments");
const deploymentMetricStatus = ref("");
const showInfoModal = ref(false);
const loaded = ref(false);
const last30DaysPercentage = ref(7.2);
const last30DaysValue = ref(26);
const last90DaysPercentage = ref(-2.5);
const last90DaysValue = ref(86);

const chartOptions = ref({
  chart: {
    height: 350,
    type: "bar",
    animations: {
      speed: 500,
      dynamicAnimation: {
        enabled: true,
        speed: 500,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  xaxis: {
    type: "datetime",
  },
  yaxis: {
    labels: {
      formatter: (value: number) => {
        return Math.trunc(value);
      },
    },
    // tickAmount: ,
    forceNiceScale: true,
  },
});

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchDeployments() {
  //set url string
  let url = import.meta.env.VITE_API_URL;

  if (props.projectName == "All") {
    url = "/metrics/deployments";
  } else {
    url =
      "/metrics/deployments?&project_name=" +
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
      deployments.value = response.data;
      if (response.data.deployment_dates.length == 0) {
        deploymentMetricStatus.value = "No Deployments";
      } else {
        deploymentMetricStatus.value = response.data.performance;
      }
      loaded.value = true;
    })
    .catch((error) => {
      console.error("GET Deployments Error: ", error);
    });
}

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

// Data used in deployments chart. Pairs of [unix timestamp, number of deployments on that day]
const deploymentsData = computed(() => {
  if (deployments.value) {
    return [
      {
        name: "Daily Deployments",
        color: "#10069f",
        data: deployments.value.deployment_dates.map((a: any) => [
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
    fetchDeployments();
  }
);

/* ----------------------------------------------
               VUE LIFECYCLE FUNCTIONS
  ---------------------------------------------- */

onMounted(() => {
  fetchDeployments();
});
</script>
