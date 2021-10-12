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
  deployment_dates: number[];
  performance: string;
  project_name: string;
  deployment_dates_description: string;
  performance_description: string;
}

export interface leadTimeItem {
  lead_time: number;
  time_units: string;
  performance: string;
  lead_time_description: string;
  performance_description: string;
  daily_commits: number[];
  daily_lead_times: number[];
}

export interface timeToRestoreItem {
  project_name: string;
  time_to_restore: number;
  performance: string;
  time_to_restore_description: string;
  performance_description: string;
  daily_times_to_restore: number[];
}

export interface changeFailureRateItem {
  project_name: string;
  change_failure_rate: number;
  change_faiure_rate_description: string;
  daily_change_failure_rates: number[];
}

export interface infoForStatusItem {
  deployments: {
    [Daily: string]: {
      info: string;
    };
    Weekly: {
      info: string;
    };
    Monthly: {
      info: string;
    };
  };

  leadTime: {
    "One Day": {
      info: string;
    };
    "One Week": {
      info: string;
    };
    "One Month": {
      info: string;
    };
    "Greater Than One Month": {
      info: string;
    };
  };

  timeToRestore: {
    "One Day": {
      info: string;
    };
    "One Week": {
      info: string;
    };
    "One Month": {
      info: string;
    };
    "Greater Than One Month": {
      info: string;
    };
  };

  changeFailureRate: {
    "0 - 15%": {
      info: string;
    };
    "16-45%": {
      info: string;
    };
    "Greater than 45%": {
      info: string;
    };
  };
}
