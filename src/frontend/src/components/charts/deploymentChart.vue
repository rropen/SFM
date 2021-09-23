<template>
  <apexchart
    ref="realtimeChart"
    type="bar"
    height="350"
    :options="chartOptions"
    :series="deploymentsData"
  ></apexchart>
</template>

<script lang="ts" setup>
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */

import { defineProps, PropType, ref, onMounted, watch, computed } from "vue";
import axios from "axios";
import { sortByMonth } from "../../utils";
import { deploymentItem } from "../../types";

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

const deployments = ref<deploymentItem>(); // holds currently fetched deployment data

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
  },
  dataLabels: {
    enabled: false,
  },
  title: {
    text: "Daily Deployments",
  },
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

function setDeploymentFreqColor() {
  if (deployments.value) {
    if (deployments.value.deployment_frequency) {
      console.log("in if");
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
    }
  } else {
    return "bg-white";
  }
}

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchDeployments() {
  //set url string
  let url = "";
  console.log("here is selcted project val: ", props.projectName);
  if (props.projectName == "All") {
    url = "metrics/deployments?category=Deployment";
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
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */

onMounted(() => {
  fetchDeployments();
});
</script>
