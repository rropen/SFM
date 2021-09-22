<template>
  <apexchart
    ref="realtimeChart"
    type="line"
    height="350"
    :options="chartOptions"
    :series="series"
  ></apexchart>
</template>

<script lang="ts" setup>
import { defineProps, PropType, ref, onMounted, watch } from "vue";
import axios from "axios";
import { sortByMonth } from "../../utils";

const props = defineProps({
  projectName: {
    type: String as PropType<string>,
    required: true,
    default: "All",
  },
  months: {
    type: Array as PropType<string[]>,
    required: false,
    default: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ],
  },
});

const series = ref([
  {
    name: "Successful Deployments",
    data: [],
  },
]);

const chartOptions = ref({
  chart: {
    height: 350,
    type: "line",
    zoom: {
      enabled: false,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "straight",
    colors: ["#10069f"],
  },
  title: {
    text: "Monthly Deployments",
    align: "left",
  },
  grid: {
    row: {
      colors: ["#f3f3f3", "transparent"], // takes an array which will be repeated on columns
      opacity: 0.5,
    },
  },
  xaxis: {
    categories: props.months,
  },
});

/* GET request to /metrics/deployments to retrieve array of deployments. */
function fetchDeployments() {
  //set url string
  let url = "";
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
      params: { all_deployments: false },
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((response) => {
      series.value[0].data = sortByMonth(response.data[0].deployment_dates);
    })
    .catch((error) => {
      console.error("GET Deployments Error: ", error);
    });
}

/* Watch to update data when changing selected project */
watch(
  () => props.projectName,
  (val, oldVal) => {
    fetchDeployments();
  }
);

onMounted(() => {
  fetchDeployments();
});
</script>
