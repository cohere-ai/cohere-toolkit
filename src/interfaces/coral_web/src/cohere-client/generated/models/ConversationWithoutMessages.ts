/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { File } from './File';
export type ConversationWithoutMessages = {
    user_id: string;
    id: string;
    created_at: string;
    updated_at: string;
    title: string;
    files: Array<File>;
    description: (string | null);
    readonly total_file_size: number;
};

