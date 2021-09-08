import { mount } from "@cypress/vue";
import Footer from "./Footer.vue";
import "../index.css";

describe("Meeting Statistics", () => {
  it("Footer is visible", () => {
    mount(Footer);
    cy.get(".wrapper")
      .should("be.visible")
      .contains("Rolls-Royce plc 2021. All rights reserved.");
  });

  it("Footer has Github, Cobalt, and Contact Us", () => {
    // This doesn't verify the link (You cant do that in cypress component tester). This makes sure the words "Github", "Cobalt" and "Contact Us" are in the component.
    mount(Footer);
    cy.contains("Contact Us").should("exist");
    cy.contains("Cobalt").should("exist");
    cy.contains("Github").should("exist");
  });
});
