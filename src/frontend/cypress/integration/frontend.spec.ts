/// <reference types="cypress" />

describe("SFM Frontend Tests", () => {
  it("Seeds Database", function () {
    cy.request("DELETE", "http://localhost:8181/utilities/clear_local_db");
    cy.request("POST", "http://localhost:8181/utilities/populate_mock_data");
    cy.wait(3000);
  });
  it("Load Home Page", function () {
    cy.visit("localhost:3000");
  });

  it("Load About Page", function () {
    cy.visit("localhost:3000/about");
  });
});
