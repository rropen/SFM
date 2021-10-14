<template>
  <div class="chartAreaWrapper flex flex-col">
    <div v-if="loaded" class="chartWrapper shadow-lg">
      <apexchart
        type="line"
        :height="chartOptions.chart.height"
        :options="chartOptions"
        :series="leadTimeData"
      ></apexchart>
    </div>
    <LoadingModal v-else :modal-height="chartOptions.chart.height + 15" />
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
        'bg-green-600 text-white': perfStatus == 'One Day',
        'bg-yellow-400 text-rrgrey-800': perfStatus == 'One Week',
        'bg-orange-500 text-white': perfStatus == 'One Month',
        'bg-red-600 text-white': perfStatus == 'Greater Than One Month',
        'bg-rrgrey-700 text-white': perfStatus == 'No pull requests to main',
      }"
    >
      <div class="spacer"></div>
      <h1 class="mx-auto text-xl">{{ perfStatus }}</h1>
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

const perfStatus = ref("One Day");
const showInfoModal = ref(false);
const modalType = ref("leadTime");
const loaded = ref(false);

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
  let url = "";
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
      },
    })
    .then((response) => {
      leadTime.value = response.data;
      perfStatus.value = response.data.performance;
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
