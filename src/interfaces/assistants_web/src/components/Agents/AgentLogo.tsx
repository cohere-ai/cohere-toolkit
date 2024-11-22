import { AgentPublic } from '@/cohere-client';
import { CoralLogo, Text } from '@/components/UI';
import { useBrandedColors } from '@/hooks';
import { cn } from '@/utils';

export const AgentLogo = ({ agent }: { agent: AgentPublic }) => {
  const isDefaultAgent = !agent.id;
  const { bg, contrastText, contrastFill } = useBrandedColors(agent.id);

  return (
    <div className={cn('flex size-5 flex-shrink-0 items-center justify-center rounded', bg)}>
      {isDefaultAgent && <CoralLogo className={cn(contrastFill, 'size-3')} />}
      {!isDefaultAgent && (
        <Text className={cn('uppercase', contrastText)} styleAs="p-sm">
          {agent.name[0]}
        </Text>
      )}
    </div>
  );
};
