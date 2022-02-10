<template>
  <div class="chartAreaWrapper flex flex-col">
    <h1 class="text-xl font-semibold text-rrgrey-700 mb-2">
      Lead Time to Change
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
          'text-green-600': perfStatus == 'One Day',
          'text-yellow-400': perfStatus == 'One Week',
          'text-orange-500': perfStatus == 'One Month',
          'text-red-600': perfStatus == 'Greater Than One Month',
          'btext-rrgrey-700': perfStatus == 'No pull requests',
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
        :series="leadTimeData"
      ></apexchart>
    </div>
    <LoadingModal v-else :modal-height="chartOptions.chart.height + 15" />

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
import { infoForStatusItem, leadTimeItem } from "../../types";
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

const leadTime = ref<leadTimeItem>(); // holds currently fetched deployment data

const perfStatus = ref("One Week");
const showInfoModal = ref(false);
const modalType = ref("leadTime");
const loaded = ref(false);
const last30DaysPercentage = ref(-1.2);
const last30DaysValue = ref(1.5);
const last90DaysPercentage = ref(2.5);
const last90DaysValue = ref(1.6);

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
        return Math.round(val);
      },
    },
  },
});

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchLeadTime() {
  //set url string
  let url = import.meta.env.VITE_API_URL;
  if (props.projectName == "All") {
    url = "/metrics/LeadTimeToChange";
  } else {
    url =
      "/metrics/LeadTimeToChange?&project_name=" +
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
      leadTime.value = response.data;
      // perfStatus.value = response.data.performance;
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
const leadTimeData = computed(() => {
  if (leadTime.value) {
    return [
      {
        name: "Time to Change (minutes)",
        color: "#10069f",
        data: leadTime.value.daily_lead_times.map((a: any) => [
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
    fetchLeadTime();
  }
);

/* ----------------------------------------------
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */

onMounted(() => {
  fetchLeadTime();
});
</script>
