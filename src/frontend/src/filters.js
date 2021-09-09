/*
Globally accessible filters to transform items in templates:
to use:
1) import filters from "./filters"
2) filters.formatDate(value) in a vue SFC template section
 */

import moment from "moment";
export default {
  formatDate(val) {
    //use this date to denote date doesn't exist
    if (val === "2100-01-01") {
      return "";
    } else {
      if (typeof val === "string") {
        return moment.unix(parseInt(val) / 1000).format("DD MMM YYYY");
      }
      return moment.unix(val / 1000).format("DD MMM YYYY");
    }
  },

  /* Function to format javascript time to time ago format */
  formatTimeAgo(val) {
    return moment(val).fromNow();
  },
};
