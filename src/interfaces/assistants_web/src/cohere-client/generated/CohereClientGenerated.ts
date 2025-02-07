import type { BaseHttpRequest } from './core/BaseHttpRequest';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { Interceptors } from './core/OpenAPI';
import { AgentService } from './services.gen';
import { AuthService } from './services.gen';
import { ChatService } from './services.gen';
import { ConversationService } from './services.gen';
import { DefaultService } from './services.gen';
import { DeploymentService } from './services.gen';
import { ExperimentalFeaturesService } from './services.gen';
import { ModelService } from './services.gen';
import { OrganizationService } from './services.gen';
import { ScimService } from './services.gen';
import { SnapshotService } from './services.gen';
import { ToolService } from './services.gen';
import { UserService } from './services.gen';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class CohereClientGenerated {
  public readonly agent: AgentService;
  public readonly auth: AuthService;
  public readonly chat: ChatService;
  public readonly conversation: ConversationService;
  public readonly default: DefaultService;
  public readonly deployment: DeploymentService;
  public readonly experimentalFeatures: ExperimentalFeaturesService;
  public readonly model: ModelService;
  public readonly organization: OrganizationService;
  public readonly scim: ScimService;
  public readonly snapshot: SnapshotService;
  public readonly tool: ToolService;
  public readonly user: UserService;

  public readonly request: BaseHttpRequest;

  constructor(
    config?: Partial<OpenAPIConfig>,
    HttpRequest: HttpRequestConstructor = FetchHttpRequest
  ) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? '',
      VERSION: config?.VERSION ?? '1.1.7',
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

    this.agent = new AgentService(this.request);
    this.auth = new AuthService(this.request);
    this.chat = new ChatService(this.request);
    this.conversation = new ConversationService(this.request);
    this.default = new DefaultService(this.request);
    this.deployment = new DeploymentService(this.request);
    this.experimentalFeatures = new ExperimentalFeaturesService(this.request);
    this.model = new ModelService(this.request);
    this.organization = new OrganizationService(this.request);
    this.scim = new ScimService(this.request);
    this.snapshot = new SnapshotService(this.request);
    this.tool = new ToolService(this.request);
    this.user = new UserService(this.request);
  }
}
