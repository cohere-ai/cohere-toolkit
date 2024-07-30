import Link from 'next/link';
import { UseFormRegister } from 'react-hook-form';

import { ASSISTANT_SETTINGS_FORM } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { Button, Input, Text, Textarea } from '@/components/Shared';
import { useIsAgentNameUnique } from '@/hooks/agents';

type Props = {
  register: UseFormRegister<ASSISTANT_SETTINGS_FORM>;
  handleNext: VoidFunction;
};

export const DefineAssistantStep: React.FC<Props> = ({ register, handleNext }) => {
  const isAgentNameUnique = useIsAgentNameUnique();

  return (
    <div className="flex flex-col space-y-3">
      <Input
        label="Name"
        placeholder="e.g., HR Benefits Bot"
        {...register('name', {
          validate: {
            uniqueName: (v) =>
              (!!v.trim() && isAgentNameUnique(v)) || 'Assistant name must be unique',
          },
        })}
      />
      <Textarea
        label="Description"
        placeholder="e.g., Answers questions about our company benefits."
        defaultRows={1}
        {...register('description')}
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
        {...register('instruction')}
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
