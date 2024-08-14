import Link from 'next/link';

import { AgentSettingsFields } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { Input, Text, Textarea } from '@/components/Shared';

type Props = {
  fields: AgentSettingsFields;
  nameError?: string;
  setFields: (fields: AgentSettingsFields) => void;
};

export const DefineAssistantStep: React.FC<Props> = ({ fields, nameError, setFields }) => {
  return (
    <div className="flex flex-col space-y-4">
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
        defaultRows={8}
        value={fields.preamble || ''}
        onChange={(e) => setFields({ ...fields, preamble: e.target.value })}
      />
    </div>
  );
};
