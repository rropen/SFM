/// <reference types="cypress" />
import { mount } from "@cypress/vue";
import infoModal from "../components/infoModal.vue";
import "../index.css";
import infoForStatus from "../views/Home.vue";

describe("Info Modal Testing", () => {
  it("Modal is visible", () => {
    const status = "Daily";
    mount(infoModal, {
      propsData: {
        status: status,
        infoForStatus: infoForStatus,
      },
    });
    cy.get(".modalBox").should("be.visible");
  });
  // it("Logo is visible", () => {
  //   mount(Header);
  //   cy.get(".w-8").should("be.visible");
  // });
});
