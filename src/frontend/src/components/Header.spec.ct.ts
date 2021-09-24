import { mount } from "@cypress/vue";
import Header from "./Header.vue";
import "../index.css";

beforeEach(() => {
  mount(Header);
});

it("Header is visible", () => {
  mount(Header);
  cy.get(".flex").should("be.visible");
});
it("Logo is visible", () => {
  mount(Header);
  cy.get(".w-8").should("be.visible");
});
