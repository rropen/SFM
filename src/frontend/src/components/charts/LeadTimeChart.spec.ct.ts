/// <reference types="cypress" />
import { mount } from "@cypress/vue";
import LeadTimeChart from "./LeadTimeChart.vue";
import "../../index.css";
import { infoForStatusItem } from "../../types";
import { walkIdentifiers } from "@vue/compiler-core";

beforeEach(() => {
  cy.intercept("GET", "**metrics/LeadTimeToChange*", {
    fixture: "leadtimes.json",
  }).as("leadtimeData");

  const projectName = "All";
  const infoForStatusValue: infoForStatusItem = {
    deployments: {
      Daily: {
        info: "The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months. For Daily, this means the median number of days with deployments per month is at least three; i.e. most working days have deployments. This corresponds to a DORA rating of Elite.",
      },
      Weekly: {
        info: "The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months. For Weekly, this means the median number of days with deployments per week is at least 1; i.e. most weeks have at least one deployment. This corresponds to a DORA rating of High.",
      },
      Monthly: {
        info: "The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months. For Monthly, this means the median number of days with deployments per month is at least one; i.e. most months have at least one deployment. This corresponds to a DORA rating of Medium.",
      },
      Yearly: {
        info: "The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months. For Yearly, this means the median number of days with deployments per month is less than one. This corresponds to a DORA rating of Low.",
      },
      "No Deployments": {
        info: "The Deployments Metric is calculated using the number of days that have had a successful deployment, or accepted pull request, to the main branch over the last three months. This project does not have any deployments over the last three months, so this metric is not applicable.",
      },
    },
    leadTime: {
      "One Day": {
        info: "The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months. For this project, the median time is less than one day. This corresponds to a DORA rating of Elite.",
      },
      "One Week": {
        info: "The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months. For this project, the median time is less than one week. This corresponds to a DORA rating of High.",
      },
      "One Month": {
        info: "The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months. For this project, the median time is less than one month. This corresponds to a DORA rating of Medium.",
      },
      "Greater Than One Month": {
        info: "The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months. For this project, the median time is greater than one month. This corresponds to a DORA rating of Low.",
      },
      "No pull requests to main": {
        info: "The Lead Time Metric is calculated using the median amount of time for a commit to be deployed into production over the last three months. For this project, there are no pull requests to main, so this metric is not applicable.",
      },
    },
    timeToRestore: {
      "Less than one hour": {
        info: "The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident). For this project, the median time is less than one hour. This corresponds to a DORA rating of Elite.",
      },
      "Less than one day": {
        info: "The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident). For this project, the median time is less than one day. This corresponds to a DORA rating of High.",
      },
      "Less than one week": {
        info: "The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident). For this project, the median time is less than one week. This corresponds to a DORA rating of Medium.",
      },
      "Between one week and one month": {
        info: "The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident). For this project, the median time is between one week and one month. This corresponds to a DORA rating of Low.",
      },
      "No closed production defects exist in the last 3 months": {
        info: "The Time To Restore Metric is calculated using the median amount of time between the deployment which caused the failure and the remediation (closing the associated bug or incident). For this project, there are no closed production defects in the last 3 months, so this metric is not relevant.",
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
  //@ts-ignore
  mount(LeadTimeChart, {
    propsData: {
      projectName: projectName,
      infoForStatus: infoForStatusValue,
    },
  });
});

it("Chart is Visible", () => {
  cy.get(".chartWrapper").should("be.visible");
  cy.get(".vue-apexcharts").should("be.visible");
  cy.get("div").contains("One Day");
});
