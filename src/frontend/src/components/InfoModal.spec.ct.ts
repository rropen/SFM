/// <reference types="cypress" />
import { mount } from "@cypress/vue";
import InfoModal from "./InfoModal.vue";
import "../index.css";
import { infoForStatusItem } from "../types";

beforeEach(() => {
  const statusValue = "Daily";
  const modalTypeValue = "deployments";
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
    leadTime: {
      "One Day": {
        info: "Less than One Day",
      },
      "One Week": {
        info: "Less than One Week",
      },
      "One Month": {
        info: "Less than One Month",
      },
      "Greater Than One Month": {
        info: "Greater than One Month",
      },
    },
  };
  //@ts-ignore
  mount(InfoModal, {
    propsData: {
      status: statusValue,
      infoForStatus: infoForStatusValue,
      modalType: modalTypeValue,
    },
  });
});

it("Modal is visible", () => {
  cy.get(".modalBox").should("be.visible");
});

it("Button Text is Correct", () => {
  cy.get("button").contains("Close");
});

it("Header Text is Correct", () => {
  cy.get("h3").contains("Daily");
});

it("Description Text is Correct", () => {
  cy.get("p").contains("Daily Info Here");
  cy.get("p").contains("First Item");
});

// Test the emit... can't figure it out - Josh 27Sep2021

// it("Close emit is sent", () => {
//   const spy = cy.spy();
//   const status = "Daily";
//   const infoForStatusValue: infoForStatusItem = {
//     deployments: {
//       Daily: {
//         info: 'Daily Info Here <ul class="list-disc"><li class="ml-8">First Item</li></ul>',
//       },
//       Weekly: {
//         info: "Weekly Info Here",
//       },
//       Monthly: {
//         info: "Monthly Info Here",
//       },
//     },
//   };
//   //@ts-ignore
//   mount(InfoModal, {
//     propsData: {
//       status: status,
//       infoForStatus: infoForStatusValue,
//     },
//     listeners: {
//       close: spy,
//     },
//   }).then(() => {
//     cy.get("button").click();
//   });
//   expect(spy).to.be.calledOnce;
// });
