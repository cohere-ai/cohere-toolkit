import Link from 'next/link';

import { AgentSettingsFields } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { Button, Input, Text, Textarea } from '@/components/Shared';
import { DEFAULT_PREAMBLE } from '@/constants';

type Props = {
  fields: AgentSettingsFields;
  nameError?: string;
  setFields: (fields: AgentSettingsFields) => void;
  handleNext: VoidFunction;
};

export const DefineAssistantStep: React.FC<Props> = ({
  fields,
  nameError,
  setFields,
  handleNext,
}) => {
  return (
    <div className="flex flex-col space-y-3">
      <Input
        label="Name"
        placeholder="e.g., HR Benefits Bot"
        value={fields.name}
        onChange={(e) => setFields({ ...fields, name: e.target.value })}
        errorText={nameError}
      />
      <Textarea
        label="Description"
        placeholder="e.g., Answers questions about our company benefits."
        defaultRows={1}
        value={fields.description ?? ''}
        onChange={(e) => setFields({ ...fields, description: e.target.value })}
      />
      <Textarea
        label="Instructions"
        labelTooltip={
          <Text>
            Learn about writing a custom assistant instructions with{' '}
            <Link
              href="https://docs.cohere.com/docs/preambles#advanced-techniques-for-writing-a-preamble"
              className="underline"
            >
              Cohere&apos;s guide
            </Link>
          </Text>
        }
        placeholder="e.g., You are friendly and helpful. You answer questions based on files in Google Drive."
        defaultRows={3}
        value={fields.preamble ?? DEFAULT_PREAMBLE}
        onChange={(e) => setFields({ ...fields, preamble: e.target.value })}
      />
      <div className="flex w-full justify-end">
        <Button
          label="Next"
          theme="evolved-green"
          kind="cell"
          icon="arrow-right"
          onClick={handleNext}
        />
      </div>
    </div>
  );
};
