/* Centralized type store used throughout the application */

import { number } from "yup";

export interface projectItem {
  name: string;
  lead_name: string;
  lead_email: string;
  description: string;
  location: string;
  repo_url: string;
  on_prem: boolean;
  id: number;
}

export interface deploymentItem {
  deploymentDates: number[];
  performance: string;
  projectName: string;
  deploymentDatesDescription: string;
  performanceDescription: string;
}

export interface leadTimeItem {
  lead_time: number;
  time_units: string;
  performance: string;
  lead_time_description: string;
  performance_description: string;
}

export interface infoForStatusItem {
  deployments: {
    Daily: {
      info: string;
    };
    Weekly: {
      info: string;
    };
    Monthly: {
      info: string;
    };
  };
}
