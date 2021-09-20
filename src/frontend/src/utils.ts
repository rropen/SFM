/// <reference types="cypress" />

/* 	Function which will take an array of dates
	and format them into an array of numbers
	
	param: dates e.g. [1624593600, 1625198400, 1625630400, 1625803200]
	return: 0-indexed array of associated months, sorted in ascending order
		e.g. [5, 5, 6, 6]
	*/
export function sortByMonth(dates: number[]) {
  const ascending = dates.sort((a, b) => a - b);
  const datesArrayByMonth = ascending.map(
    (val) => new Date(val * 1000).getMonth() // or toDateString()
  );
  const datesBinned = sortDataIntoMonthBins(datesArrayByMonth);
  return datesBinned;
}

/* 	Function which will reformat an array of months into bins

	param: ArrayOfMonths e.g. [0, 4, 2, 10] = [Jan, May, Mar, Nov]
	return: 0-indexed bin of months e.g. [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0]
*/
export function sortDataIntoMonthBins(arrayOfMonths: number[]) {
  var bins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

  for (let i = 0; i < arrayOfMonths.length; i += 1) {
    bins[arrayOfMonths[i]] += 1;
  }
  return bins;
}
