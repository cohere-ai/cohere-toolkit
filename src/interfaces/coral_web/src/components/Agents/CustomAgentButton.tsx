import Link from 'next/link';

import { Text } from '@/components/Shared';

type Props = {
  id: string;
  name: string;
};
/**
 * @description renders a button to navigate to a user created knowledge agent page.
 */
export const CustomAgentButton: React.FC<Props> = ({ id, name }) => {
  return (
    <Link className="group h-8 w-8 rounded border border-marble-500 p-[1px]" href={`/agents/${id}`}>
      <div className="flex h-full w-full items-center justify-center rounded bg-secondary-400 transition-colors duration-300 group-hover:bg-secondary-500">
        <Text className="uppercase">{name[0] || ''}</Text>;
      </div>
    </Link>
  );
};
