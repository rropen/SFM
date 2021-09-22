/// <reference types="cypress" />
// var date = new Date();
describe("SFM Frontend Tests", () => {
  const dayjs = require("dayjs");
  const todaysDate = dayjs().format("YYYY-MM-DD");
  const todaysDateConfirm = dayjs().format("DD MMM YYYY");
  const historicalDate = dayjs().subtract(60, "day").format("YYYY-MM-DD");
  const historicalDateConfirm = dayjs()
    .subtract(60, "day")
    .format("DD MMM YYYY");
  it("Load Home Page", function () {
    cy.visit("localhost:3000");
  });

  it("Load About Page", function () {
    cy.visit("localhost:3000/about");
  });
});
