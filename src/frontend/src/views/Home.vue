<template>
  <div class="h-screen flex overflow-hidden bg-gray-100">
    <TransitionRoot as="template" :show="sidebarOpen">
      <Dialog
        as="div"
        class="fixed inset-0 flex z-40 md:hidden"
        @close="sidebarOpen = false"
      >
        <TransitionChild
          as="template"
          enter="transition-opacity ease-linear duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity ease-linear duration-300"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <DialogOverlay class="fixed inset-0 bg-rrgrey-800 bg-opacity-95" />
        </TransitionChild>
        <TransitionChild
          as="template"
          enter="transition ease-in-out duration-300 transform"
          enter-from="-translate-x-full"
          enter-to="translate-x-0"
          leave="transition ease-in-out duration-300 transform"
          leave-from="translate-x-0"
          leave-to="-translate-x-full"
        >
          <div class="relative flex-1 flex flex-col max-w-xs w-full bg-white">
            <TransitionChild
              as="template"
              enter="ease-in-out duration-300"
              enter-from="opacity-0"
              enter-to="opacity-100"
              leave="ease-in-out duration-300"
              leave-from="opacity-100"
              leave-to="opacity-0"
            >
              <div class="absolute top-0 right-0 -mr-12 pt-2">
                <!-- Close Sidebar Button -->
                <button
                  type="button"
                  class="
                    ml-1
                    flex
                    items-center
                    justify-center
                    h-10
                    w-10
                    rounded-full
                    bg-rrgrey-800
                    ring-2 ring-inset ring-rrblue-400
                  "
                  @click="sidebarOpen = false"
                >
                  <span class="sr-only">Close sidebar</span>
                  <XIcon class="h-6 w-6 text-rrblue-400" aria-hidden="true" />
                </button>
              </div>
            </TransitionChild>
            <div class="flex-1 h-0 pb-4 overflow-y-auto">
              <h1
                class="
                  mx-auto
                  text-center
                  mt-5
                  text-2xl
                  font-semibold
                  text-rrgrey-800
                "
              >
                DORA<br />Metrics
              </h1>
              <p
                class="
                  mx-auto
                  mt-2
                  text-center text-rrblue-800
                  underline
                  text-sm
                "
              >
                Learn More
              </p>
              <nav class="mt-5 px-2 space-y-1">
                <rrDropdown
                  label="Project"
                  :choices="projectDropdownChoices"
                  :selected="selectedProject"
                  @updatedChoice="changeProject"
                />
                <rrDropdown
                  label="Timescale"
                  :choices="timescaleChoices"
                  :selected="selectedTimescale"
                  @updatedChoice="changeTimescale"
                />
              </nav>
            </div>
          </div>
        </TransitionChild>
        <div class="flex-shrink-0 w-14">
          <!-- Force sidebar to shrink to fit close icon -->
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Static sidebar for desktop -->
    <div class="hidden md:flex md:flex-shrink-0">
      <div class="flex flex-col w-64">
        <!-- Sidebar component, swap this element with another sidebar if you like -->
        <div class="flex-1 flex flex-col min-h-0 bg-white shadow-lg">
          <div class="flex-1 flex flex-col pb-4 overflow-y-auto">
            <h1
              class="
                mx-auto
                text-center
                mt-5
                text-2xl
                font-semibold
                text-rrgrey-800
              "
            >
              DORA<br />Metrics
            </h1>
            <p
              class="mx-auto mt-2 text-center text-rrblue-800 underline text-sm"
            >
              Learn More
            </p>
            <nav class="mt-5 flex-1 px-2 bg-white space-y-1">
              <rrDropdown
                label="Project"
                :choices="projectDropdownChoices"
                :selected="selectedProject"
                @updatedChoice="changeProject"
              />
              <rrDropdown
                label="Timescale"
                :choices="timescaleChoices"
                :selected="selectedTimescale"
                @updatedChoice="changeTimescale"
              />
            </nav>
          </div>
        </div>
      </div>
    </div>
    <div class="flex flex-col w-0 flex-1 overflow-hidden">
      <div class="md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3">
        <button
          type="button"
          class="
            -ml-0.5
            -mt-0.5
            h-12
            w-12
            inline-flex
            items-center
            justify-center
            rounded-md
            text-rrgrey-600
            hover:text-rrgrey-800
            focus:outline-none
            focus:ring-2
            focus:ring-inset
            focus:ring-rrblue-400
          "
          @click="sidebarOpen = true"
        >
          <span class="sr-only">Open sidebar</span>
          <MenuIcon class="h-6 w-6" aria-hidden="true" />
        </button>
      </div>
      <main
        class="
          flex-1
          relative
          z-0
          overflow-y-auto
          focus:outline-none
          bg-rrgrey-200
        "
      >
        <div class="py-6">
          <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-14">
            <!-- Replace with your content -->
            <div class="py-4">
              <div class="rounded-lg h-96">
                <div v-if="dataLoaded" class="shadow-xl p-4" id="chart">
                  <apexchart
                    type="line"
                    height="350"
                    :options="chartOptions"
                    :series="series"
                  ></apexchart>
                </div>
                <div v-else>Loading Data...</div>
                <div
                  class="
                    flex
                    box-content
                    h-12
                    w-5/12
                    p-4
                    my-6
                    mx-auto
                    rounded-full
                    text-4xl
                    justify-center
                  "
                  :class="deploymentTimescaleColor"
                >
                  Current Rating: {{ deploymentTimescale }}
                </div>
              </div>
            </div>
            <!-- /End replace -->
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */
import { ref, onMounted, computed, watch } from "vue";
import { deploymentItem, projectItem } from "../types";
import { rrDropdown } from "@rrglobal/vue-cobalt";
import VueApexCharts from "vue3-apexcharts";
import axios from "axios";
import {
  Dialog,
  DialogOverlay,
  TransitionChild,
  TransitionRoot,
} from "@headlessui/vue";
import {
  CalendarIcon,
  ChartBarIcon,
  FolderIcon,
  HomeIcon,
  InboxIcon,
  MenuIcon,
  UsersIcon,
  XIcon,
} from "@heroicons/vue/outline";
import { setMapStoreSuffix } from "pinia";
import { sortByMonth } from "../utils";

/* ----------------------------------------------
                     CONSTANTS
// ---------------------------------------------- */

const timescaleChoices = ["All Time", "Monthly", "Weekly", "Daily"];

const months = [
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
];

const dataLoaded = ref(false);

// let testDataPTS = [];
// let testDataPTSAverage = [];

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */
const deploymentTimescale = ref("Monthly");
const deploymentTimescaleColor = ref("");
const sidebarOpen = ref(false);
const selectedProject = ref("All");
const selectedTimescale = ref(timescaleChoices[1]);

const projects = ref<projectItem[]>([]); // holds all fetched projects
const deployments = ref<deploymentItem>(); // holds currently fetched deployment data

const dataHolder = getData();

const series = ref([
  {
    name: "Daily Deployments",
    // type: 'column',
    data: dataHolder[0],
  },
  {
    name: "4-day Rolling Average",
    type: "line",
    color: "#10069f",
    data: dataHolder[0],
  },
]);

// const chartOptions = ref({
//   chart: {
//     type: 'line',
//     // type: 'bar',
//     height: 350,
//   },
//   dataLabels: {
//     enabled: false,
//   },
//   plotOptions: {
//     bar: {
//       fill: {
//         type: 'gradient',
//         gradient: {
//           shade: 'dark',
//           type: 'horizontal',
//           shadeIntensity: 0.5,
//           gradientToColors: undefined,
//           inverseColors: true,
//           opacityFrom: 0.2,
//           opacityTo: 1,
//           stops: [0, 50, 100],
//           colorStops: [],
//         },
//       },
//       columnWidth: '50%',
//       // distributed: true,
//       // width: '10%'
//       // color: "#4f98ff",
//       colors: {
//         ranges: [
//           {
//             color: '#4f98ff',
//           },
//         ],
//         backgroundBarOpacity: 0.5,
//       },
//     },
//   },
//   // dataLabels: {},
//   // fill: false,
//   // area: {
//   //   fill: false
//   // }
//   // },
//   // columnWidth: '15%',
//   xaxis: {
//     type: 'datetime',
//     tickAmount: 12,
//   },
//   yaxis: {
//     formatter: (val) => {
//       return val.toFixed(2);
//     },
//     tickAmount: 4,
//     max: 4,
//     decimalsInFloat: 0,
//   },
//   tooltip: {
//     shared: true,
//     intersect: false,
//     x: {
//       format: 'dd MMM yyyy',
//     },
//   },
//   stroke: {
//     curve: 'smooth',
//     // width: '10%'
//   },
// });

const chartOptions = ref({
  chart: {
    height: 350,
    type: "line",
  },
  stroke: {
    width: [0, 5],
    curve: "smooth",
  },
  title: {
    text: "Successful Deployments",
  },
  plotOptions: {
    // bar: {
    //   columnWidth: '10%',
    // },
  },
  // color: '#10069f',

  xaxis: {
    type: "datetime",
    // tickAmount: 10,
  },
  yaxis: {
    formatter: (val) => {
      return val.toFixed(2);
    },
    tickAmount: 4,
    max: 12,
    decimalsInFloat: 0,
  },
});

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

/* List of Strings including "All" then all fetched project names */
const projectDropdownChoices = computed(() => {
  let dropdownChoices = projects.value.map((a) => a.name);
  dropdownChoices.unshift("All");
  selectedProject.value = dropdownChoices[0]; //set initial value
  // console.log(dropdownChoices);
  return dropdownChoices;
});

/* ----------------------------------------------
                     WATCHERS
  ---------------------------------------------- */

/* Demo watcher to track a changing variable... delete me later */
watch(selectedTimescale, (val, oldVal) => {
  console.log("Selected Timescale: ");
  console.log("was: ", oldVal);
  console.log("Is: ", val);
});

/* Watch to update data when changing selected project */
watch(selectedProject, (val, oldVal) => {
  if (oldVal) {
    // console.log(deploymentsData.value);
    fetchDeployments();
  }
});

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */
function getData() {
  let testDataPTS = [];
  let testDataPTSAverage = [];
  let currCounter = 1609992559;
  for (let i = 0; i < 35; i++) {
    testDataPTS.push([currCounter, Math.floor(10 * Math.random())]);
    // testDataPTS.push([currCounter,3])
    currCounter += 7 * 86400;
  }
  console.log("here is test pts", testDataPTS);
  // console.log('test data pts', testDataPTS);
  for (let i = 0; i < 35; i++) {
    if (i < 7) {
      testDataPTSAverage.push([testDataPTS[i][0], testDataPTS[i][1]]);
      // console.log(i, testDataPTSAverage)
      // } else if (i > 196) {
      //   console.log('got here')
      //   testDataPTSAverage.push([testDataPTS[i][0], testDataPTS[i][1]])
      // } else {
    } else {
      // console.log('got here');
      let sum = 0;
      sum =
        testDataPTS[i][1] +
        testDataPTS[i - 1][1] +
        testDataPTS[i - 2][1] +
        testDataPTS[i - 3][1] +
        testDataPTS[i - 4][1] +
        testDataPTS[i - 5][1] +
        testDataPTS[i - 6][1];
      testDataPTSAverage.push([testDataPTS[i][0], sum / 7]);
      // console.log(i, testDataPTSAverage)
    }
  }
  // console.log('test data pts avg: ', testDataPTSAverage);
  let retval1 = testDataPTSAverage.map((a) => [new Date(a[0] * 1000), a[1]]);
  // console.log(ret)
  let retval2 = testDataPTS.map((a) => [new Date(a[0] * 1000), a[1]]);
  return [retval2, retval1];
  // return sortedData;
}

function fetchDeployments() {
  console.log("fetch deployments called");
  console.log(selectedProject.value);
  //set url string
  let url = "";
  if (selectedProject.value == "All") {
    url = "charts/test?category=Deployment";
  } else {
    url =
      "charts/test?category=Deployment&project_name=" +
      encodeURIComponent(selectedProject.value);
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
      console.log("in then of fetchDeployments");
      deployments.value = response.data[0];
      deploymentTimescale.value = setDeploymentTimescale(
        response.data[0].deployment_frequency
      );
      console.log("here is series value before: ", series.value);
      console.log("here is series value: ", series.value);
    })
    .catch((error) => {
      console.error("GET Deployments Error: ", error);
    });
}

/* GET request to /projects to retrieve array of projects. */
const fetchProjects = () => {
  console.log("fetch projects called");
  axios
    .get("projects", {
      params: { skip: 0, limit: 100 },
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((response) => {
      projects.value = response.data;
    })
    .catch((error) => {
      console.error("GET Projects Error: ", error);
    });
};

function setDeploymentTimescale(str) {
  let rating = "";
  switch (str) {
    case "Daily":
      rating = "Elite";
      deploymentTimescaleColor.value = "bg-bggreen";
      break;
    case "Weekly":
      rating = "High";
      deploymentTimescaleColor.value = "bg-bgyellow";
      break;
    case "Monthly":
      rating = "Medium";
      deploymentTimescaleColor.value = "bg-bgorange";
      break;
    case "Yearly":
      rating = "Low";
      deploymentTimescaleColor.value = "bg-red-600";
      break;
    default:
      rating = "No data";
  }
  return rating;
}

/* Manage changes from project dropdown  */
function changeProject(val: string) {
  selectedProject.value = val;
}

/* Manage changes from timescale dropdown */
function changeTimescale(val: string) {
  selectedTimescale.value = val;
}

/* ----------------------------------------------
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */
onMounted(() => {
  fetchDeployments();
  fetchProjects();
  dataLoaded.value = true;
});
</script>
