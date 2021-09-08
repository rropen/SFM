// var date = new Date();
describe("MEC Frontend Tests", () => {
  const dayjs = require("dayjs");
  const todaysDate = dayjs().format("YYYY-MM-DD");
  it("Load Home Page", function () {
    cy.visit("localhost:3000");
  });

  // it("Load About Page", function () {
  //   cy.visit("localhost:3000/about");
  // });

  // Inputs data into the data table then compares that data to the table output farther down

  // it("Inputing Data into table", function () {

  //   cy.moment().format('DD','MM','YYYY')
  //   cy.visit("localhost:3000");
  //   cy.get("#employeeNumber").clear();
  //   cy.get("#employeeNumber").type("5426");
  //   cy.get("#meetingTitle").clear();
  //   cy.get("#meetingTitle").type("Test Meeting Title");
  //   cy.get("#numSlides").clear();
  //   cy.get("#numSlides").type(9635);
  //   cy.get("#meetingGroup").clear();
  //   cy.get("#meetingGroup").type("Group Test abc123");
  //   cy.get("#comment").clear();
  //   cy.get("#comment").type("Test Comment");
  //   cy.get("#start").click().wait(100);
  //   cy.get("#stop").click();
  //   cy.get("#submit").click();
  // });

  // it("Verify Data in dataTable", function () {
  //   cy.get("#dataTable").contains("Test Meeting Title");
  //   cy.get("#dataTable").contains("5426");
  //   cy.get("#dataTable").contains("9635");
  //   cy.get("#dataTable").contains("Group Test abc123");
  //   cy.get("#dataTable").contains("Test Comment");
  //   cy.get("#dataTable").contains("1.");
  // });

  it("Past Meeting Form", function () {
    // cy.clock();
    cy.get("#employeeNumber").clear();
    cy.get("#pastMeeting").click();
    cy.get("#pastMeetingTitle").type("Past Meeting Title");
    cy.get("#pastMeetingGroup").type("Past Meeting Group");
    cy.get("#pastMeetingDate").type(todaysDate);
    cy.get("#pastMeetingComment").type("Past Meeting Comment");
    cy.get("#pastMeetingEmployeeNumber").clear().type("999");
    cy.get("#pastMeetingMinutes").clear().type("888");
    cy.get("#pastMeetingNumSlides").clear().type("777");
    cy.get("#pastMeetingSubmit").click();
  });

  // it("Verify Past Meeting data in Table", function () {
  //   cy.get("#dataTable").contains("Past Meeting Title");
  //   cy.get("#dataTable").contains("999");
  //   cy.get("#dataTable").contains("888");
  //   cy.get("#dataTable").contains("777");
  //   cy.get("#dataTable").contains("1996002");
  //   cy.get("#dataTable").contains("21 Jan 2021");
  //   cy.get("#dataTable").contains("Past Meeting Group");
  //   cy.get("#dataTable").contains("Past Meeting Comment");
  // });

  // it("Verifies data displayed in total statistics", function () {
  //   cy.get("#totalButton").click();
  //   cy.get("#totalClicked").contains("444");
  //   cy.get("#totalTime").contains("888");
  //   cy.get("#totalCost").contains("199600");
  //   cy.get("#averageCost").contains("99800");
  //   cy.get("#totalSlides").contains("10412");
  // });

  // it("Verifies data displayed in last 30 days statistics", function () {
  //   cy.get("#daysButton").click();
  //   cy.get("#totalClicked").contains("0");
  //   cy.get("#totalTime").contains("0");
  //   cy.get("#totalCost").contains("1.");
  //   cy.get("#averageCost").contains("1.");
  //   cy.get("#totalSlides").contains("9635");
  // });

  // it("Deletes Past Meeting Data From Table", function () {
  //   cy.get("#deleteButton").click();
  //   cy.get("#confirmDelete").click();
  //   cy.get("#deleteButton").click();
  //   cy.get("#confirmDelete").click();
  //   cy.reload();
  //   cy.get("#dataTable").should("not.have.text", "Past Meeting Comment");
  //   cy.get("#dataTable").should("not.have.text", "Test Comment");
  // });
});
