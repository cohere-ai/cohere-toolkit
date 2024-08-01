import { Document } from '@/cohere-client';
import { IconName } from '@/components/Shared';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';

type PythonInterpreterFieldsBase = {
  snippet?: string; // citation snippet, will either be the stdout, stderr, or the file name
};

type PythonInterpreterImageFields = {
  /**
   * String representation of a json object with the following fields:
   * - filename: string
   * - b64_data: string
   */
  output_file?: string;
};

type PythonInterpreterCodeFields = {
  code_runtime?: string;
  success?: string; // "True" or "False"
  std_out?: string;
  std_err?: string;
  /**
   * String representation of a json object with the following fields:
   * - type: string (e.g. "ZeroDivisionError")
   * - message: string (usually a stack trace)
   */
  error?: string;
};

type PythonInterpreterFields = PythonInterpreterFieldsBase &
  PythonInterpreterImageFields &
  PythonInterpreterCodeFields;

export type PythonInterpreterOutputFile = { filename: string; b64_data: string };
export type PythonInterpreterCodeError = { type: string; message: string };

export const parsePythonInterpreterToolFields = (document: Document) => {
  if (!document.fields) {
    return {
      snippet: undefined,
      success: undefined,
      codeRuntime: undefined,
      stdErr: undefined,
      stdOut: undefined,
      error: undefined,
      outputFile: undefined,
    };
  }

  const fields = document.fields as PythonInterpreterFields;
  let outputFile: PythonInterpreterOutputFile | undefined;
  let error: PythonInterpreterCodeError | undefined;

  if (fields.output_file) {
    try {
      outputFile = JSON.parse(fields.output_file);
    } catch (e) {
      console.error('Could not parse output_file', e);
    }
  }

  if (fields.error) {
    try {
      error = JSON.parse(fields.error);
    } catch (e) {
      console.error('Could not parse error', e);
    }
  }

  return {
    snippet: fields.snippet,
    success: fields.success ? fields.success.toLowerCase() === 'true' : undefined,
    codeRuntime: fields.code_runtime,
    stdErr: fields.std_err,
    stdOut: fields.std_out,
    error,
    outputFile,
  };
};

export const getToolIcon = (toolId?: string | null): IconName => {
  return TOOL_ID_TO_DISPLAY_INFO[toolId ?? '']?.icon ?? TOOL_FALLBACK_ICON;
};
