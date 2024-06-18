/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
<<<<<<< HEAD
import type { AgentDeployment } from './AgentDeployment';
import type { AgentModel } from './AgentModel';
import type { ToolName } from './ToolName';

=======
>>>>>>> b840c79b5fbeaf115fd0390f5c2d63efb1161cf0
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
<<<<<<< HEAD
  tools: Array<ToolName>;
  model: AgentModel;
  deployment: AgentDeployment;
=======
  tools: Array<string>;
  model: string;
  deployment: string;
>>>>>>> b840c79b5fbeaf115fd0390f5c2d63efb1161cf0
};
