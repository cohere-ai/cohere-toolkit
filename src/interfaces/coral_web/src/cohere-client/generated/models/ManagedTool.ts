/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { Category } from './Category';

export type ManagedTool = {
  name: string;
  display_name?: string;
  description?: string | null;
  parameter_definitions?: Record<string, any> | null;
  kwargs?: Record<string, any>;
  is_visible?: boolean;
  is_available?: boolean;
  error_message?: string | null;
  category?: Category;
  is_auth_required?: boolean;
  auth_url?: string | null;
};
