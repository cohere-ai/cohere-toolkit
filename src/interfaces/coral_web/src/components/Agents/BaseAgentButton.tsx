import Link from 'next/link';

import { CoralLogo } from '@/components/Shared';

/**
 * @description renders a button to navigate to the default knowledge agent page.
 */
export const BaseAgentButton: React.FC = () => {
  return (
    <Link className="group h-8 w-8 rounded border border-marble-500 p-[1px]" href="/agents">
      <div className="flex h-full w-full items-center justify-center rounded bg-secondary-400 transition-colors duration-300 group-hover:bg-secondary-500">
        <CoralLogo style="secondary" />
      </div>
    </Link>
  );
};
