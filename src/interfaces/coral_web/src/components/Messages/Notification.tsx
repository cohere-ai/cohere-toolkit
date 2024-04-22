import { Transition } from '@headlessui/react';

import { Text } from '@/components/Shared';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { cn } from '@/utils';

type Props = { message: string; show: boolean; shouldAnimate?: boolean; className?: string };

const Notification: React.FC<Props> = ({
  message,
  show,
  shouldAnimate = false,
  className = '',
}) => {
  const { welcomeGuideState } = useWelcomeGuideState();
  const isOnboarding = welcomeGuideState !== WelcomeGuideStep.DONE;

  return (
    <Transition
      show={show}
      appear={shouldAnimate}
      className={cn('relative mx-4 md:mx-28', className)}
      enter={cn('transition-all duration-300', {
        'ease-out': isOnboarding,
      })}
      enterFrom={cn('opacity-0 ', { 'translate-y-2': isOnboarding })}
      enterTo={cn('opacity-100', { 'translate-y-0': isOnboarding })}
      leave={cn('transition-all duration-300', {
        'ease-out': isOnboarding,
      })}
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <div className="absolute inset-0 flex items-center" aria-hidden="true">
        <div className="w-full border-t border-marble-400" />
      </div>
      <div className="relative flex justify-center">
        <Text as="span" className="bg-marble-100 px-2 text-volcanic-600">
          {message}
        </Text>
      </div>
    </Transition>
  );
};
export default Notification;
