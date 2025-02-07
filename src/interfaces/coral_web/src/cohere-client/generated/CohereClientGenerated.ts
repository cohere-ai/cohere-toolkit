import type { BaseHttpRequest } from './core/BaseHttpRequest';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { Interceptors } from './core/OpenAPI';
import { DefaultService } from './services.gen';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class CohereClientGenerated {
  public readonly default: DefaultService;

  public readonly request: BaseHttpRequest;

  constructor(
    config?: Partial<OpenAPIConfig>,
    HttpRequest: HttpRequestConstructor = FetchHttpRequest
  ) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? '',
      VERSION: config?.VERSION ?? '0.1.0',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
      interceptors: {
        request: config?.interceptors?.request ?? new Interceptors(),
        response: config?.interceptors?.response ?? new Interceptors(),
      },
    });

    this.default = new DefaultService(this.request);
  }
}
