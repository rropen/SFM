<template>
  <div class="flex bg-gray-100">
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
                    ring-2 ring-inset ring-white
                  "
                  @click="sidebarOpen = false"
                >
                  <span class="sr-only">Close sidebar</span>
                  <XIcon class="h-6 w-6 text-white" aria-hidden="true" />
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
                  v-if="loaded"
                  label="Project"
                  :choices="projectDropdownChoices"
                  :selected="selectedProject"
                  @updatedChoice="changeProject"
                />
                <LoadingModal v-else />
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
                v-if="loaded"
                label="Project"
                :choices="projectDropdownChoices"
                :selected="selectedProject"
                @updatedChoice="changeProject"
              />
              <LoadingModal v-else />
            </nav>
          </div>
        </div>
      </div>
    </div>
    <div class="flex flex-col w-0 flex-1 overflow-auto">
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
      <main class="flex-1 relative z-0 focus:outline-none bg-rrgrey-200">
        <div class="py-6">
          <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-14">
            <!-- Replace with your content -->
            <div class="py-4">
              <div
                class="
                  grid grid-flow-col grid-cols-1 grid-rows-4
                  2xl:grid-cols-2 2xl:grid-rows-2
                  gap-4
                  2xl:gap-6
                "
              >
                <div class="m-4 xl:m-6 p-4">
                  <h1 class="text-3xl font-semibold text-rrgrey-700 mb-2">
                    Deployments
                  </h1>
                  <DeploymentChart
                    :projectName="selectedProject"
                    :infoForStatus="infoForStatus"
                  />
                </div>
                <div class="m-4 xl:m-6 p-4">
                  <h1 class="text-3xl font-semibold text-rrgrey-700 mb-2">
                    Time To Restore
                  </h1>
                  <TimeToRestoreChart
                    :projectName="selectedProject"
                    :infoForStatus="infoForStatus"
                  />
                </div>
                <div class="m-4 xl:m-6 p-4">
                  <h1 class="text-3xl font-semibold text-rrgrey-700 mb-2">
                    Lead Time to Change
                  </h1>
                  <LeadTimeChart
                    :projectName="selectedProject"
                    :infoForStatus="infoForStatus"
                  />
                </div>
                <div class="m-4 xl:m-6 p-4">
                  <h1 class="text-3xl font-semibold text-rrgrey-700 mb-2">
                    Change Failure Rate
                  </h1>
                  <ChangeFailureRateChart
                    :projectName="selectedProject"
                    :infoForStatus="infoForStatus"
                  />
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
import { ref, onMounted, computed, watch, onBeforeMount } from "vue";
import { deploymentItem, infoForStatusItem, projectItem } from "../types";
import { rrDropdown } from "@rrglobal/vue-cobalt";
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
import DeploymentChart from "../components/charts/DeploymentChart.vue";
import LeadTimeChart from "../components/charts/LeadTimeChart.vue";
import TimeToRestoreChart from "../components/charts/TimeToRestoreChart.vue";
import ChangeFailureRateChart from "../components/charts/ChangeFailureRateChart.vue";
import LoadingModal from "../components/LoadingModal.vue";

/* ----------------------------------------------
                     CONSTANTS
// ---------------------------------------------- */

/* ----------------------------------------------
                  VARIABLES
---------------------------------------------- */

const sidebarOpen = ref(false);
const selectedProject = ref("All");
const loaded = ref(false);

const projects = ref<projectItem[]>([]); // holds all fetched projects
const infoForStatus: infoForStatusItem = {
  deployments: {
    Daily: {
      info: "For this project, the median number of days with deployments per week is at least three, i.e. the majority of working days have a deployment. This corresponds to a DORA rating of <span class='text-green-600 font-bold'>Elite </span>. <br><br> The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months.",
    },
    Weekly: {
      info: "For this project, the median number of days with deployments per week is at least one. This corresponds to a DORA rating of <span class='text-yellow-300 font-bold'>High </span>. <br><br> The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months.",
    },
    Monthly: {
      info: "For this project, the median number of days with deployments per week is less than one. This corresponds to a DORA rating of <span class='text-orange-600 font-bold'>Medium</span>. <br><br> The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months.",
    },
    Yearly: {
      info: "For this project, the median number of days with deployments per month is less than one. This corresponds to a DORA rating of <span class='text-red-600 font-bold'>Low</span>. <br><br> The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months.",
    },
    "No Deployments": {
      info: "This project does not have any deployments over the last three months, so this metric is <span class='text-black font-bold'> not relevant</span>.<br><br>The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months.",
    },
  },
  leadTime: {
    "One Day": {
      info: "For this project, the median lead time to deploy is less than one day. This corresponds to a DORA rating of <span class='text-green-600 font-bold'>Elite</span>. <br><br> The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months.",
    },
    "One Week": {
      info: "For this project, the median lead time to deploy is less than one week. This corresponds to a DORA rating of <span class='text-yellow-300 font-bold'>High</span>. <br><br> The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months.",
    },
    "One Month": {
      info: "For this project, the median lead time to deploy is less than one month. This corresponds to a DORA rating of <span class='text-orange-600 font-bold'>Medium</span>. <br><br> The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months.",
    },
    "Greater Than One Month": {
      info: "For this project, the median lead time to deploy is greater than one month. This corresponds to a DORA rating of <span class='text-red-600 font-bold'>Low</span>. <br><br> The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months.",
    },
    "No pull requests to main": {
      info: "For this project, there are no pull requests to main, so this metric is <span class='text-black font-bold'>not relevant</span>. <br><br> The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months.",
    },
  },
  timeToRestore: {
    "Less than one hour": {
      info: "For this project, the median time to restore is less than one hour. This corresponds to a DORA rating of <span class='text-green-600 font-bold'>Elite</span>. <br><br> The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident).",
    },
    "Less than one day": {
      info: "For this project, the median time to restore is less than one day. This corresponds to a DORA rating of <span class='text-yellow-300 font-bold'>High</span>. <br><br> The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident).",
    },
    "Less than one week": {
      info: "For this project, the median time to restore is less than one week. This corresponds to a DORA rating of <span class='text-orange-600 font-bold'>Medium</span>. <br><br> The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident).",
    },
    "Between one week and one month": {
      info: "For this project, the median time to restore is between one week and one month. This corresponds to a DORA rating of <span class='text-red-600 font-bold'>Low</span>. <br><br> The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident).",
    },
    "No closed production defects exist in the last 3 months": {
      info: "For this project, there are no closed production defects in the last 3 months, so this metric is <span class='text-black font-bold'>not relevant</span>. <br><br> The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident).",
    },
  },
  changeFailureRate: {
    High: {
      info: "The Change Failure Rate Metric is calculated as the number of failed deployments per total number of deployments over the last three months. A rate of 0-15% corresponds to DORA Elite/High, A rate of 16-45% corresponds to DORA Medium, and a rate higher than 45% corresponds to DORA Low.",
    },
    Medium: {
      info: "The Change Failure Rate Metric is calculated as the number of failed deployments per total number of deployments over the last three months. A rate of 0-15% corresponds to DORA Elite/High, A rate of 16-45% corresponds to DORA Medium, and a rate higher than 45% corresponds to DORA Low.",
    },
    Low: {
      info: "The Change Failure Rate Metric is calculated as the number of failed deployments per total number of deployments over the last three months. A rate of 0-15% corresponds to DORA Elite/High, A rate of 16-45% corresponds to DORA Medium, and a rate higher than 45% corresponds to DORA Low.",
    },
  },
};

/* ----------------------------------------------
                      COMPUTED
  ---------------------------------------------- */

/* List of Strings including "All" then all fetched project names */
const projectDropdownChoices = computed(() => {
  let dropdownChoices = projects.value.map((a) => a.name);
  dropdownChoices.unshift("All");
  selectedProject.value = dropdownChoices[0]; //set initial value
  return dropdownChoices;
});

/* ----------------------------------------------
                     WATCHERS
  ---------------------------------------------- */

/* ----------------------------------------------
                    FUNCTIONS
---------------------------------------------- */

/* GET request to /projects to retrieve array of projects. */
// let bearer = import.meta.env.VITE_API_AUTH_TOKEN;
const fetchProjects = () => {
  axios
    .get("/projects", {
      params: { skip: 0, limit: 100 },
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${import.meta.env.VITE_API_AUTH_TOKEN}`,
        // Authorization: 'Bearer ' + bearer,
      },
    })
    .then((response) => {
      projects.value = response.data;
      loaded.value = true;
    })
    .catch((error) => {
      console.error("GET Projects Error: ", error);
    });
};

/* Manage changes from project dropdown  */
function changeProject(val: string) {
  selectedProject.value = val;
}

/* ----------------------------------------------
               VUE BUILT-IN FUNCTIONS
  ---------------------------------------------- */
onMounted(() => {
  fetchProjects();
  loaded.value = true;
});
</script>
