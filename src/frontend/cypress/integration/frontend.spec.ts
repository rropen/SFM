/// <reference types="cypress" />

describe("SFM Frontend Tests", () => {
  it("Seeds Database", function () {
    cy.request("DELETE", "http://localhost:8181/utilities/clear_local_db");
    cy.visit("localhost:8181/docs");
    cy.request("POST", "http://localhost:8181/utilities/populate_mock_data");
  });
  it("Load Home Page", function () {
    cy.visit("localhost:3000");
  });

  it("Load About Page", function () {
    cy.visit("localhost:3000/about");
  });

  /* ==== Test Created with Cypress Studio ==== */
  it("Test Project Dropdown", function () {
    /* ==== Generated with Cypress Studio ==== */
    cy.visit("http://localhost:3000/");
    cy.get("#location").select("Project for Deployments Testing");
    /* ==== End Cypress Studio ==== */
  });

  /* ==== Test Created with Cypress Studio ==== */
  it("Test Deployments Status Bar Modal", function () {
    /* ==== Generated with Cypress Studio ==== */
    cy.visit("localhost:3000");
    cy.get(":nth-child(1) > .chartAreaWrapper > .mt-4 > .mr-4 > path").click();
    cy.get(".modalBox").click();
    cy.get(".delay-100").click();
    /* ==== End Cypress Studio ==== */
  });
});
