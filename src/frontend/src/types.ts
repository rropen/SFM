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
