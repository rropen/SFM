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
                Dora<br />Metrics
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
                <a
                  v-for="item in NAVIGATION"
                  :key="item.name"
                  :href="item.href"
                  :class="[
                    item.current
                      ? 'bg-white text-rrgrey-800'
                      : 'text-rrgrey-600 ',
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                  ]"
                >
                  <component
                    :is="item.icon"
                    :class="[
                      item.current
                        ? 'text-rrgrey-800'
                        : 'text-rrgrey-600 group-hover:text-rrgrey-600',
                      'mr-3 flex-shrink-0 h-6 w-6',
                    ]"
                    aria-hidden="true"
                  />
                  {{ item.name }}
                </a>
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
              Dora<br />Metrics
            </h1>
            <p
              class="mx-auto mt-2 text-center text-rrblue-800 underline text-sm"
            >
              Learn More
            </p>
            <nav class="mt-5 flex-1 px-2 bg-white space-y-1">
              <a
                v-for="item in NAVIGATION"
                :key="item.name"
                :href="item.href"
                :class="[
                  item.current
                    ? 'bg-white text-rrgrey-800'
                    : 'text-rrgrey-600 ',
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                ]"
              >
                <component
                  :is="item.icon"
                  :class="[
                    item.current
                      ? 'text-rrgrey-800'
                      : 'text-rrgrey-600 group-hover:text-rrgrey-600',
                    'mr-3 flex-shrink-0 h-6 w-6',
                  ]"
                  aria-hidden="true"
                />
                {{ item.name }}
              </a>
              <rrDropdown
                label="Project"
                :choices="projectDropdownChoices"
                :selected="initialProjectChoice"
                @updatedChoice="onChange"
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
            <h1 class="text-2xl font-semibold text-rrgrey-900">Project Name</h1>
          </div>
          <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-14">
            <!-- Replace with your content -->
            <div class="py-4">
              <div
                class="border-4 border-dashed border-gray-200 rounded-lg h-96"
              >
                <div id="chart">
                  <apexchart
                    ref="realtimeChart"
                    type="line"
                    height="350"
                    :options="chartOptions"
                    :series="series"
                  ></apexchart>
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
import { ref, onMounted } from "vue";
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

/* ----------------------------------------------
                GLOBAL VARIABLES
---------------------------------------------- */

const CONNECTION_STRING = "http://localhost:8181/";

const NAVIGATION = [
  { name: "Dashboard", href: "#", icon: HomeIcon, current: true },
  { name: "Team", href: "#", icon: UsersIcon, current: false },
  { name: "Projects", href: "#", icon: FolderIcon, current: false },
  { name: "Calendar", href: "#", icon: CalendarIcon, current: false },
  { name: "Documents", href: "#", icon: InboxIcon, current: false },
  { name: "Reports", href: "#", icon: ChartBarIcon, current: false },
];

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */
const projectDropdownChoices = ref([]);

const initialProjectChoice = ref("All");

const series = ref([
  {
    name: "Successful Deployments",
    data: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
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
    categories: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ],
  },
});

const sidebarOpen = ref(false);

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */
function setProjectDropdownChoicesWrapper() {
  axios.get(CONNECTION_STRING + "projects").then((res) => {
    projectDropdownChoices.value = setProjectDropdownChoices(res);
  });
}

function setProjectDropdownChoices(resp) {
  console.log("here is the response: ", resp);
  let arr = ["All"];
  for (let ele of resp.data) {
    arr.push(ele.name);
  }
  return arr;
}

function onChange(val: string) {
  formatDeploymentDataWrapper();
}

function formatDeploymentDataWrapper() {
  axios.get("http://localhost:8181/charts?category=Deployment").then((res) => {
    series.value[0].data = formatDeploymentData(res);
  });
}

function formatDeploymentData(res) {
  let data = res.data.deployment_dates;
  let monthArr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  for (let ele of data) {
    ele = ele.slice(5, 7);
    switch (ele) {
      case "01":
        monthArr[0]++;
        break;
      case "02":
        monthArr[1]++;
        break;
      case "03":
        monthArr[2]++;
        break;
      case "04":
        monthArr[3]++;
        break;
      case "05":
        monthArr[4]++;
        break;
      case "06":
        monthArr[5]++;
        break;
      case "07":
        monthArr[6]++;
        break;
      case "08":
        monthArr[7]++;
        break;
      case "09":
        monthArr[8]++;
        break;
      case "10":
        monthArr[9]++;
        break;
      case "11":
        monthArr[10]++;
        break;
      case "12":
        monthArr[11]++;
        break;
    }
  }
  return monthArr;
}

/* ----------------------------------------------
             VUE BUILT-IN FUNCTIONS
---------------------------------------------- */
onMounted(() => {
  setProjectDropdownChoicesWrapper();
  formatDeploymentDataWrapper();
});
</script>
