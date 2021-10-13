<template>
  <div class="chartAreaWrapper flex flex-col">
    <div v-if="loaded" class="chartWrapper shadow-lg">
      <apexchart
        ref="realtimeChart"
        type="bar"
        :height="chartOptions.chart.height"
        :options="chartOptions"
        :series="deploymentsData"
      ></apexchart>
    </div>
    <LoadingModal :modal-height="chartOptions.chart.height + 15" v-else />
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
        'bg-green-600 text-white': deploymentMetricStatus == 'Daily',
        'bg-yellow-400 text-rrgrey-800': deploymentMetricStatus == 'Weekly',
        'bg-orange-500 text-white': deploymentMetricStatus == 'Monthly',
        'bg-red-600 text-white': deploymentMetricStatus == 'Yearly',
        'bg-rrgrey-700 text-white': deploymentMetricStatus == 'Not Applicable',
      }"
    >
      <div class="spacer"></div>
      <h1 class="mx-auto text-xl">{{ deploymentMetricStatus }}</h1>
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
  let url = "";
  if (props.projectName == "All") {
    url = "metrics/deployments";
  } else {
    url =
      "metrics/deployments?&project_name=" +
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
      // console.log('resp', response.data)
      deployments.value = response.data[0];
      loaded.value = true;
      if (response.data[0].deployment_dates.length == 0) {
        deploymentMetricStatus.value = "Not Applicable";
      } else {
        deploymentMetricStatus.value = response.data[0].performance;
      }
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
