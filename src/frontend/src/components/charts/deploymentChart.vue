<template>
  <div class="chartAreaWrapper flex flex-col">
    <div class="chartWrapper shadow-lg">
      <apexchart
        ref="realtimeChart"
        type="bar"
        height="350"
        :options="chartOptions"
        :series="deploymentsData"
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
        'bg-green-600 text-white': deploymentMetricStatus == 'Daily',
        'bg-yellow-400 text-rrgrey-800': deploymentMetricStatus == 'Weekly',
        'bg-orange-500 text-white': deploymentMetricStatus == 'Monthly',
        'bg-red-600 text-white': deploymentMetricStatus == 'Yearly',
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
      >
      </infoModal>
    </teleport>
  </div>
</template>

<script lang="ts" setup>
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */

import { defineProps, PropType, ref, onMounted, watch, computed } from "vue";
import axios from "axios";

import { sortByMonth } from "../../utils";
import { deploymentItem, infoForStatusItem } from "../../types";
import infoModal from "../infoModal.vue";

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
const deploymentMetricStatus = ref("");
const showInfoModal = ref(false);

// Sample data for generating chart. Will be deleted when endpoint is working
function getData() {
  let testDataPTS = [];
  let currCounter = 1609992559;
  for (let i = 0; i < 200; i++) {
    testDataPTS.push([currCounter, Math.floor(4 * Math.random())]);
    currCounter += 86400;
  }
  let retval = testDataPTS.map((a) => [new Date(a[0] * 1000), a[1]]);
  return retval;
}

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
  // title: {
  //   text: "Daily Deployments",
  // },
  xaxis: {
    type: "datetime",
  },
  yaxis: {
    labels: {
      formatter: (value) => {
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
      params: {
        all_deployments: false,
      },
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((response) => {
      deployments.value = response.data[0];
      deploymentMetricStatus.value = response.data[0].deployment_frequency;
    })
    .catch((error) => {
      console.error("GET Deployments Error: ", error);
    });
}

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

const deploymentFreqColorComputed = computed(() => {
  if (deployments.value) {
    switch (deployments.value.deployment_frequency) {
      case "Daily":
        return "bg-bggreen";
      case "Weekly":
        return "bg-bgyellow";
      case "Monthly":
        return "bg-bgorange";
      case "Yearly":
        return "bg-red-600";
    }
  } else {
    return "bg-white";
  }
});

// Data used in deployments chart. Pairs of [unix timestamp, number of deployments on that day]
const deploymentsData = computed(() => {
  if (deployments.value) {
    return [
      {
        name: "Daily Deployments",
        color: "#10069f",
        data: getData(), //This can be changed to the data from the endpoint once it is refactored
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
