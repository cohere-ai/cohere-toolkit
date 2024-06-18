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
export type CreateAgent = {
  name: string;
  version?: number | null;
  description?: string | null;
  preamble?: string | null;
  temperature?: number | null;
<<<<<<< HEAD
  model: AgentModel;
  deployment: AgentDeployment;
  tools?: Array<ToolName> | null;
=======
  model: string;
  deployment: string;
  tools?: Array<string> | null;
>>>>>>> b840c79b5fbeaf115fd0390f5c2d63efb1161cf0
};
