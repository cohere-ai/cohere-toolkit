/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatRole } from './ChatRole';
/**
 * A list of previous messages between the user and the model, meant to give the model conversational context for responding to the user's message.
 */
export type ChatMessage = {
    role: ChatRole;
    message: string;
};

