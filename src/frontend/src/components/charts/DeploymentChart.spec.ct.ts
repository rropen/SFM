/// <reference types="cypress" />
import { mount } from "@cypress/vue";
import DeploymentChart from "./DeploymentChart.vue";
import "../../index.css";
import { infoForStatusItem } from "../../types";

beforeEach(() => {
  // add a div for modal to attach to
  cy.document().then((document) => {
    document.body.innerHTML += '<div id="modals"></div>';
  });
  cy.intercept("GET", "/deployments*", { fixture: "deployments.json" });

  const projectName = "Project1";
  const infoForStatusValue: infoForStatusItem = {
    deployments: {
      Daily: {
        info: 'Daily Info Here <ul class="list-disc"><li class="ml-8">First Item</li></ul>',
      },
      Weekly: {
        info: "Weekly Info Here",
      },
      Monthly: {
        info: "Monthly Info Here",
      },
    },
  };
  //@ts-ignore
  mount(DeploymentChart, {
    propsData: {
      projectName: projectName,
      infoForStatus: infoForStatusValue,
    },
  });
});

it("Chart is Visible", () => {
  cy.get(".chartWrapper").should("be.visible");
});

// it("Close emit is sent", () => {
//   cy.get("button").contains("Close");
// });

// it("Proper Text is Visible", () => {
//   cy.get("h3").contains("Daily");
// });

// it("Proper Text is Visible", () => {
//   cy.get("p").contains("Daily Info Here");
//   cy.get("p").contains("First Item");
// });
