import { Transition } from '@headlessui/react';

import { StartOptionKey, StartOptions } from '@/components/Messages/Welcome/StartOptions';
import { useShowWelcomeGuide } from '@/hooks/ftux';
import { cn } from '@/utils';

type Props = {
  show: boolean;
  startOption: StartOptionKey;
  onStartOptionChange: (option: StartOptionKey) => void;
};

/**
 * Renders the welcome message that animates in at the start of a new conversation.
 */
const Welcome: React.FC<Props> = ({ show, startOption, onStartOptionChange }) => {
  const showRAGFTUX = useShowWelcomeGuide();

  return (
    <Transition
      show={show}
      appear
      enter={cn({
        'transition-all duration-300 ease-out delay-500': showRAGFTUX,
      })}
      enterFrom={cn({ 'opacity-0 translate-y-2': showRAGFTUX })}
      enterTo={cn({ 'opacity-100 translate-y-0': showRAGFTUX })}
      leave="transition-opacity duration-500 delay-500"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      className="flex flex-col"
    >
      <StartOptions selectedOption={startOption} onOptionSelect={onStartOptionChange} />
    </Transition>
  );
};

export default Welcome;
