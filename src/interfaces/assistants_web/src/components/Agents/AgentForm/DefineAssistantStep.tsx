import {
  AgentFormFieldKeys,
  CreateAgentFormFields,
  UpdateAgentFormFields,
} from '@/components/Agents/AgentForm/AgentForm';
import { Button, Input, Textarea } from '@/components/Shared';

type Props<K extends UpdateAgentFormFields | CreateAgentFormFields> = {
  fields: K;
  setFields: React.Dispatch<React.SetStateAction<K>>;
  errors?: Partial<Record<AgentFormFieldKeys, string>>;
  isAgentCreator: boolean;
  setCurrentStep: (currentStep: number) => void;
};

export function DefineAssistantStep<K extends CreateAgentFormFields | UpdateAgentFormFields>({
  fields,
  setFields,
  errors,
  isAgentCreator,
  setCurrentStep,
}: Props<K>) {
  return (
    <div className="flex flex-col space-y-4">
      <Input
        label="Name"
        placeholder="e.g., HR Benefits Bot"
        value={fields.name ?? ''}
        onChange={(e) => setFields((prev) => ({ ...prev, name: e.target.value }))}
        errorText={errors?.name}
        disabled={!isAgentCreator}
      />
      <Textarea
        label="Description"
        placeholder="e.g., Answers questions about our company benefits."
        value={fields.description ?? ''}
        defaultRows={1}
        onChange={(e) => setFields((prev) => ({ ...prev, description: e.target.value }))}
        disabled={!isAgentCreator}
      />
      <Textarea
        label="Instruction (Optional)"
        placeholder="e.g., You are friendly and helpful. You answer questions based on files in Google Drive."
        value={fields.preamble ?? ''}
        defaultRows={1}
        onChange={(e) => setFields((prev) => ({ ...prev, preamble: e.target.value }))}
        disabled={!isAgentCreator}
      />
      {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
      <Button className="ml-auto w-fit" label="Next" onClick={() => setCurrentStep(1)} />
    </div>
  );
}
