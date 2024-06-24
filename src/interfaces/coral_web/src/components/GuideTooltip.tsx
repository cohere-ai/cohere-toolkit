import { Transition } from '@headlessui/react';
import React from 'react';

import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  currentStep: number;
  totalSteps: number;
  title: string;
  description: string;
  buttonLabel: string;
  onNext: VoidFunction;
  onClose: VoidFunction;
  show?: boolean;
  className?: string;
};

/**
 * A tooltip that guides the user through a series of onboarding steps.
 */
export const GuideTooltip: React.FC<Props> = ({
  className = '',
  show = false,
  title,
  description,
  buttonLabel,
  currentStep,
  totalSteps,
  onNext,
  onClose,
}) => {
  return (
    <Transition
      show={show}
      appear
      as="div"
      className={cn(
        'absolute z-guide-tooltip',
        'h-fit w-[260px] sm:w-[305px]',
        'rounded border border-primary-200 bg-primary-100',
        'transition-opacity duration-300 ease-out',
        'flex flex-col gap-y-3 py-2.5',
        className
      )}
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <div className="flex gap-x-4 pl-4 pr-2">
        <Text className="flex flex-col pt-2" as="span">
          <span className="font-medium">{title}</span>
          {description}
        </Text>
        <button
          className={cn(
            'flex h-4 w-4 items-center rounded',
            'text-primary-800 transition-colors ease-in-out hover:text-primary-700',
            'focus:outline-none focus-visible:outline-1 focus-visible:outline-offset-1 focus-visible:outline-volcanic-900'
          )}
          onClick={onClose}
        >
          <Icon name="close" />
        </button>
      </div>

      <div className="flex items-center justify-between px-4">
        <Text styleAs="p-xs" className="text-volcanic-800">
          {currentStep} of {totalSteps}
        </Text>
        <button
          className={cn(
            'rounded px-2.5 py-0.5 text-primary-50 ',
            'bg-primary-800 transition-colors ease-in-out hover:bg-primary-700',
            'focus:outline-none focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900'
          )}
          onClick={onNext}
        >
          <Text styleAs="overline">{buttonLabel}</Text>
        </button>
      </div>
    </Transition>
  );
};
