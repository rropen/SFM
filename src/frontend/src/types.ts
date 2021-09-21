/* Centralized type store used throughout the application */

import { number } from "yup";

export interface meetingItem {
  id?: number;
  comment: string;
  date: number;
  employeeNumber: number;
  groupCost: number;
  meetingGroup: string;
  meetingId: string;
  powerpointSlides: number;
  time: number;
  title: string;
  totalCost: number;
}

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
