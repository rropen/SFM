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
  deployment_dates: Array<number>;
  deployment_frequency: string;
  project_name: string;
}

export interface leadTimeItem {
  lead_time: number;
  time_units: string;
  performance: string;
  lead_time_description: string;
  performance_description: string;
}
