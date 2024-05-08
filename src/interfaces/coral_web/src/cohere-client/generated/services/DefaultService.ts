/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
import type { Body_upload_file_conversations_upload_file_post } from '../models/Body_upload_file_conversations_upload_file_post';
import type { Body_upload_file_with_conversation_conversations__conversation_id__upload_file_post } from '../models/Body_upload_file_with_conversation_conversations__conversation_id__upload_file_post';
import type { ChatResponseEvent } from '../models/ChatResponseEvent';
import type { CohereChatRequest } from '../models/CohereChatRequest';
import type { Conversation } from '../models/Conversation';
import type { ConversationWithoutMessages } from '../models/ConversationWithoutMessages';
import type { CreateUser } from '../models/CreateUser';
import type { DeleteConversation } from '../models/DeleteConversation';
import type { DeleteFile } from '../models/DeleteFile';
import type { DeleteUser } from '../models/DeleteUser';
import type { Deployment } from '../models/Deployment';
import type { File } from '../models/File';
import type { LangchainChatRequest } from '../models/LangchainChatRequest';
import type { ListFile } from '../models/ListFile';
import type { ManagedTool } from '../models/ManagedTool';
import type { NonStreamedChatResponse } from '../models/NonStreamedChatResponse';
import type { UpdateConversation } from '../models/UpdateConversation';
import type { UpdateDeploymentEnv } from '../models/UpdateDeploymentEnv';
import type { UpdateFile } from '../models/UpdateFile';
import type { UpdateUser } from '../models/UpdateUser';
import type { UploadFile } from '../models/UploadFile';
import type { User } from '../models/User';

export class DefaultService {
  /**
   * Chat Stream
   * Stream chat endpoint to handle user messages and return chatbot responses.
   *
   * Args:
   * session (DBSessionDep): Database session.
   * chat_request (CohereChatRequest): Chat request data.
   * request (Request): Request object.
   *
   * Returns:
   * EventSourceResponse: Server-sent event response with chatbot responses.
   * @returns ChatResponseEvent Successful Response
   * @throws ApiError
   */
  public static chatStreamChatStreamPost({
    requestBody,
  }: {
    requestBody: CohereChatRequest;
  }): CancelablePromise<Array<ChatResponseEvent>> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/chat-stream',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Chat
   * Chat endpoint to handle user messages and return chatbot responses.
   *
   * Args:
   * chat_request (CohereChatRequest): Chat request data.
   * session (DBSessionDep): Database session.
   * request (Request): Request object.
   *
   * Returns:
   * NonStreamedChatResponse: Chatbot response.
   * @returns NonStreamedChatResponse Successful Response
   * @throws ApiError
   */
  public static chatChatPost({
    requestBody,
  }: {
    requestBody: CohereChatRequest;
  }): CancelablePromise<NonStreamedChatResponse> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/chat',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Langchain Chat Stream
   * @returns any Successful Response
   * @throws ApiError
   */
  public static langchainChatStreamLangchainChatPost({
    requestBody,
  }: {
    requestBody: LangchainChatRequest;
  }): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/langchain-chat',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create User
   * Create a new user.
   *
   * Args:
   * user (CreateUser): User data to be created.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * User: Created user.
   * @returns User Successful Response
   * @throws ApiError
   */
  public static createUserUsersPost({
    requestBody,
  }: {
    requestBody: CreateUser;
  }): CancelablePromise<User> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/users/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List Users
   * List all users.
   *
   * Args:
   * offset (int): Offset to start the list.
   * limit (int): Limit of users to be listed.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * list[User]: List of users.
   * @returns User Successful Response
   * @throws ApiError
   */
  public static listUsersUsersGet({
    offset,
    limit = 100,
  }: {
    offset?: number;
    limit?: number;
  }): CancelablePromise<Array<User>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/users/',
      query: {
        offset: offset,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get User
   * Get a user by ID.
   *
   * Args:
   * user_id (str): User ID.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * User: User with the given ID.
   *
   * Raises:
   * HTTPException: If the user with the given ID is not found.
   * @returns User Successful Response
   * @throws ApiError
   */
  public static getUserUsersUserIdGet({ userId }: { userId: string }): CancelablePromise<User> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/users/{user_id}',
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update User
   * Update a user by ID.
   *
   * Args:
   * user_id (str): User ID.
   * new_user (UpdateUser): New user data.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * User: Updated user.
   *
   * Raises:
   * HTTPException: If the user with the given ID is not found.
   * @returns User Successful Response
   * @throws ApiError
   */
  public static updateUserUsersUserIdPut({
    userId,
    requestBody,
  }: {
    userId: string;
    requestBody: UpdateUser;
  }): CancelablePromise<User> {
    return __request(OpenAPI, {
      method: 'PUT',
      url: '/users/{user_id}',
      path: {
        user_id: userId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete User
   * "
   * Delete a user by ID.
   *
   * Args:
   * user_id (str): User ID.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * DeleteUser: Empty response.
   *
   * Raises:
   * HTTPException: If the user with the given ID is not found.
   * @returns DeleteUser Successful Response
   * @throws ApiError
   */
  public static deleteUserUsersUserIdDelete({
    userId,
  }: {
    userId: string;
  }): CancelablePromise<DeleteUser> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/users/{user_id}',
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Conversation
   * "
   * Get a conversation by ID.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * session (DBSessionDep): Database session.
   * request (Request): Request object.
   *
   * Returns:
   * Conversation: Conversation with the given ID.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns Conversation Successful Response
   * @throws ApiError
   */
  public static getConversationConversationsConversationIdGet({
    conversationId,
  }: {
    conversationId: string;
  }): CancelablePromise<Conversation> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/conversations/{conversation_id}',
      path: {
        conversation_id: conversationId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Conversation
   * Update a conversation by ID.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * new_conversation (UpdateConversation): New conversation data.
   * session (DBSessionDep): Database session.
   * request (Request): Request object.
   *
   * Returns:
   * Conversation: Updated conversation.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns Conversation Successful Response
   * @throws ApiError
   */
  public static updateConversationConversationsConversationIdPut({
    conversationId,
    requestBody,
  }: {
    conversationId: string;
    requestBody: UpdateConversation;
  }): CancelablePromise<Conversation> {
    return __request(OpenAPI, {
      method: 'PUT',
      url: '/conversations/{conversation_id}',
      path: {
        conversation_id: conversationId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Conversation
   * Delete a conversation by ID.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * session (DBSessionDep): Database session.
   * request (Request): Request object.
   *
   * Returns:
   * DeleteConversation: Empty response.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns DeleteConversation Successful Response
   * @throws ApiError
   */
  public static deleteConversationConversationsConversationIdDelete({
    conversationId,
  }: {
    conversationId: string;
  }): CancelablePromise<DeleteConversation> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/conversations/{conversation_id}',
      path: {
        conversation_id: conversationId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List Conversations
   * List all conversations.
   *
   * Args:
   * offset (int): Offset to start the list.
   * limit (int): Limit of conversations to be listed.
   * session (DBSessionDep): Database session.
   * request (Request): Request object.
   *
   * Returns:
   * list[ConversationWithoutMessages]: List of conversations.
   * @returns ConversationWithoutMessages Successful Response
   * @throws ApiError
   */
  public static listConversationsConversationsGet({
    offset,
    limit = 100,
  }: {
    offset?: number;
    limit?: number;
  }): CancelablePromise<Array<ConversationWithoutMessages>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/conversations',
      query: {
        offset: offset,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Upload File With Conversation
   * (TO BE DEPRECATED)
   *
   *
   * Uploads a file to a conversation.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * session (DBSessionDep): Database session.
   * file (FastAPIUploadFile): File to be uploaded.
   *
   * Returns:
   * UploadFile: Uploaded file.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found. Status code 404.
   * HTTPException: If the file wasn't uploaded correctly. Status code 500.
   * @returns UploadFile Successful Response
   * @throws ApiError
   */
  public static uploadFileWithConversationConversationsConversationIdUploadFilePost({
    conversationId,
    formData,
  }: {
    conversationId: string;
    formData: Body_upload_file_with_conversation_conversations__conversation_id__upload_file_post;
  }): CancelablePromise<UploadFile> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/conversations/{conversation_id}/upload_file',
      path: {
        conversation_id: conversationId,
      },
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Upload File
   * Uploads and creates a File object.
   * If no conversation_id is provided, a new Conversation is created as well.
   *
   * Args:
   * session (DBSessionDep): Database session.
   * file (FastAPIUploadFile): File to be uploaded.
   * conversation_id (Optional[str]): Conversation ID passed from request query parameter.
   *
   * Returns:
   * UploadFile: Uploaded file.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found. Status code 404.
   * HTTPException: If the file wasn't uploaded correctly. Status code 500.
   * @returns UploadFile Successful Response
   * @throws ApiError
   */
  public static uploadFileConversationsUploadFilePost({
    formData,
  }: {
    formData: Body_upload_file_conversations_upload_file_post;
  }): CancelablePromise<UploadFile> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/conversations/upload_file',
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List Files
   * List all files from a conversation. Important - no pagination support yet.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * list[ListFile]: List of files from the conversation.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns ListFile Successful Response
   * @throws ApiError
   */
  public static listFilesConversationsConversationIdFilesGet({
    conversationId,
  }: {
    conversationId: string;
  }): CancelablePromise<Array<ListFile>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/conversations/{conversation_id}/files',
      path: {
        conversation_id: conversationId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update File
   * Update a file by ID.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * file_id (str): File ID.
   * new_file (UpdateFile): New file data.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * File: Updated file.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns File Successful Response
   * @throws ApiError
   */
  public static updateFileConversationsConversationIdFilesFileIdPut({
    conversationId,
    fileId,
    requestBody,
  }: {
    conversationId: string;
    fileId: string;
    requestBody: UpdateFile;
  }): CancelablePromise<File> {
    return __request(OpenAPI, {
      method: 'PUT',
      url: '/conversations/{conversation_id}/files/{file_id}',
      path: {
        conversation_id: conversationId,
        file_id: fileId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete File
   * Delete a file by ID.
   *
   * Args:
   * conversation_id (str): Conversation ID.
   * file_id (str): File ID.
   * session (DBSessionDep): Database session.
   *
   * Returns:
   * DeleteFile: Empty response.
   *
   * Raises:
   * HTTPException: If the conversation with the given ID is not found.
   * @returns DeleteFile Successful Response
   * @throws ApiError
   */
  public static deleteFileConversationsConversationIdFilesFileIdDelete({
    conversationId,
    fileId,
  }: {
    conversationId: string;
    fileId: string;
  }): CancelablePromise<DeleteFile> {
    return __request(OpenAPI, {
      method: 'DELETE',
      url: '/conversations/{conversation_id}/files/{file_id}',
      path: {
        conversation_id: conversationId,
        file_id: fileId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List Tools
   * List all available tools.
   *
   * Returns:
   * list[ManagedTool]: List of available tools.
   * @returns ManagedTool Successful Response
   * @throws ApiError
   */
  public static listToolsToolsGet(): CancelablePromise<Array<ManagedTool>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/tools',
    });
  }
  /**
   * List Deployments
   * List all available deployments and their models.
   *
   * Returns:
   * list[Deployment]: List of available deployment options.
   * @returns Deployment Successful Response
   * @throws ApiError
   */
  public static listDeploymentsDeploymentsGet({
    all = false,
  }: {
    all?: boolean;
  }): CancelablePromise<Array<Deployment>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/deployments',
      query: {
        all: all,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Set Env Vars
   * Set environment variables for the deployment.
   *
   * Returns:
   * str: Empty string.
   * @returns any Successful Response
   * @throws ApiError
   */
  public static setEnvVarsDeploymentsNameSetEnvVarsPost({
    name,
    requestBody,
  }: {
    name: string;
    requestBody: UpdateDeploymentEnv;
  }): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/deployments/{name}/set_env_vars',
      path: {
        name: name,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List Experimental Features
   * List all experimental features and if they are enabled
   *
   * Returns:
   * Dict[str, bool]: Experimental feature and their isEnabled state
   * @returns any Successful Response
   * @throws ApiError
   */
  public static listExperimentalFeaturesExperimentalFeaturesGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/experimental_features/',
    });
  }
  /**
   * Health
   * Health check for backend APIs
   * @returns any Successful Response
   * @throws ApiError
   */
  public static healthHealthGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/health',
    });
  }
  /**
   * Apply Migrations
   * Applies Alembic migrations - useful for serverless applications
   * @returns any Successful Response
   * @throws ApiError
   */
  public static applyMigrationsMigratePost(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/migrate',
    });
  }
}
