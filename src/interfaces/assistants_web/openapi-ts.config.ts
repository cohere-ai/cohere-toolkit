import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://0.0.0.0:8000/openapi.json',
  output: './src/cohere-client/generated',
  name: 'CohereClientGenerated',
  types: {
    enums: 'typescript',
  },
  services: {
    asClass: true,
  },
});
