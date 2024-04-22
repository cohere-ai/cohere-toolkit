import { RadioGroup } from '@headlessui/react';
import React from 'react';

import { StartOptionKey } from '@/components/Messages/Welcome/StartOptions';
import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  value: StartOptionKey;
  title: string;
  description: string;
  features: string[];
};

/**
 * @description A card displaying information about a start option
 */
export const OptionCard: React.FC<Props> = ({ value, title, description, features }) => {
  return (
    <RadioGroup.Option value={value} className="w-full md:w-96 md:shrink">
      {({ checked }) => (
        <div
          className={cn(
            'flex h-full w-full cursor-pointer flex-col items-start gap-y-4 px-4 py-6 transition ',
            'rounded-md border',
            'border-marble-500',
            { 'border-volcanic-800': checked }
          )}
        >
          <div
            className={cn('flex rounded-md px-4 py-2 text-white transition', 'bg-primary-300', {
              'bg-primary-500': checked,
            })}
          >
            <RadioGroup.Label>
              <Text styleAs="h5" className="text-white">
                {title}
              </Text>
            </RadioGroup.Label>
          </div>
          <RadioGroup.Description>
            <Text as="span">{description}</Text>
          </RadioGroup.Description>
          <div className="h-px w-full bg-marble-500" />
          <Text styleAs="label">Best for</Text>
          <ul>
            {features.map((item) => (
              <li key={item} className="flex gap-x-2">
                <Icon name="check-mark" className="mt-0.5" /> <Text>{item}</Text>
              </li>
            ))}
          </ul>
        </div>
      )}
    </RadioGroup.Option>
  );
};
