/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { File } from './File';
import type { Message } from './Message';
export type Conversation = {
    user_id: string;
    id: string;
    created_at: string;
    updated_at: string;
    title: string;
    messages: Array<Message>;
    files: Array<File>;
    description: (string | null);
    readonly total_file_size: number;
};

