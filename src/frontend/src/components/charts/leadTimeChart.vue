<template>
  <apexchart
    type="line"
    height="350"
    :options="chartOptions"
    :series="leadTimeData"
  ></apexchart>
</template>

<script lang="ts" setup>
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */

import { defineProps, PropType, ref, onMounted, watch, computed } from "vue";
import axios from "axios";
import { leadTimeItem } from "../../types";

/* ----------------------------------------------
                  PROPS
---------------------------------------------- */

const props = defineProps({
  projectName: {
    type: String as PropType<string>,
    required: true,
    default: "All",
  },
});

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */

const leadTime = ref<leadTimeItem>(); // holds currently fetched deployment data

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
function fetchLeadTime() {
  //set url string
  let url = "";
  if (props.projectName == "All") {
    url = "metrics/LeadTimeToChange";
  } else {
    url =
      "metrics/LeadTimeToChange?&project_name=" +
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
        data: leadTime.value.daily_lead_times.map((a) => [
          new Date(a[0] * 1000),
          a[1],
        ]), //getData(), //This can be changed to the data from the endpoint once it is refactored
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
