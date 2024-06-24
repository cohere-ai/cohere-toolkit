/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type Agent = {
  user_id: string;
  organization_id?: string | null;
  id: string;
  created_at: string;
  updated_at: string;
  version: number;
  name: string;
  description: string | null;
  preamble: string | null;
  temperature: number;
  tools: Array<string>;
  model: string;
  deployment: string;
};
