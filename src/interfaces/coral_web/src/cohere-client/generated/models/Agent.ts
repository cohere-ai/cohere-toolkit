/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AgentDeployment } from './AgentDeployment';
import type { AgentModel } from './AgentModel';
import type { ToolName } from './ToolName';

export type Agent = {
  user_id: string;
  id: string;
  created_at: string;
  updated_at: string;
  version: number;
  name: string;
  description: string | null;
  preamble: string | null;
  temperature: number;
  tools: Array<ToolName>;
  model: AgentModel;
  deployment: AgentDeployment;
};
