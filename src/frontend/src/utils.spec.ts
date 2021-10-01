/// <reference types="cypress" />

import { sortByMonth, sortDataIntoMonthBins } from "./utils";

/* sortByMonth Testing */
describe("Unit Testing for SortByMonth function", function () {
  before(() => {
    expect(sortByMonth, "sortByMonth").to.be.a("function");
  });
  context("", function () {
    const input = [1624593600, 1625198400, 1625630400, 1625803200];
    it("can sort by month", function () {
      expect(JSON.stringify(sortByMonth(input))).to.eq(
        JSON.stringify([0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0])
      );
    });
  });
});

/* sortDataIntoMonthBins Testing */
describe("Unit Testing for sortDataIntoMonthBins function", function () {
  before(() => {
    expect(sortDataIntoMonthBins, "sortDataIntoMonthBins").to.be.a("function");
  });
  context("", function () {
    const input = [1, 1, 1, 4, 4, 11, 11, 11, 11, 0];
    it("can put month array into bins", function () {
      expect(JSON.stringify(sortDataIntoMonthBins(input))).to.eq(
        JSON.stringify([1, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 4])
      );
    });
  });
});
