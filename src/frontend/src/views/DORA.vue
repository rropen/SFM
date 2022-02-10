<template>
  <div class="flex bg-white">
    <Sidebar />
    <div class="flex flex-col w-0 flex-1 overflow-auto">
      <main>
        <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-14">
          <DeploymentChart
            class="mt-10"
            :projectName="selectedProject"
            :infoForStatus="infoForStatus"
          />

          <TimeToRestoreChart
            class="mt-4"
            :projectName="selectedProject"
            :infoForStatus="infoForStatus"
          />

          <LeadTimeChart
            class="mt-4"
            :projectName="selectedProject"
            :infoForStatus="infoForStatus"
          />

          <ChangeFailureRateChart
            class="mt-4"
            :projectName="selectedProject"
            :infoForStatus="infoForStatus"
          />
          <!-- /End replace -->
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
/* ----------------------------------------------
                  IMPORTS
---------------------------------------------- */
import { ref, onMounted, computed } from "vue";
import { infoForStatusItem, projectItem } from "../types";
import axios from "axios";

import DeploymentChart from "../components/charts/DeploymentChart.vue";
import LeadTimeChart from "../components/charts/LeadTimeChart.vue";
import TimeToRestoreChart from "../components/charts/TimeToRestoreChart.vue";
import ChangeFailureRateChart from "../components/charts/ChangeFailureRateChart.vue";
import Sidebar from "../components/Sidebar.vue";

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
