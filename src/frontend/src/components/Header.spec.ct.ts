/// <reference types="cypress" />
import { mount } from "@cypress/vue";
import Header from "./Header.vue";
import "../index.css";

beforeEach(() => {
  //@ts-ignore
  mount(Header);
});

it("Header is visible", () => {
  cy.get(".flex").should("be.visible");
});

it("Logo is visible", () => {
  cy.get("img").should("be.visible");
});
