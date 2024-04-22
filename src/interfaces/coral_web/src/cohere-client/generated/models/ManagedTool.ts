/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Category } from './Category';

export type ManagedTool = {
  name: string;
  description?: string | null;
  parameter_definitions?: Record<string, any> | null;
  kwargs?: Record<string, any>;
  is_visible?: boolean;
  category?: Category;
};
