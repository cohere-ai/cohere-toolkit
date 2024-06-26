import { OpenAPI, ToolkitClient } from './generated';

export * from './generated/index';

export const client = new ToolkitClient(OpenAPI);
