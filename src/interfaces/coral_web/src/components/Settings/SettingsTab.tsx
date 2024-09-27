'use client';

import { Dropdown, InputLabel, STYLE_LEVEL_TO_CLASSES, Slider, Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { useModels } from '@/hooks/deployments';
import { useSettingsDefaults } from '@/hooks/settings';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';

/**
 * @description Settings tab to adjust endpoint params like preamble and temperature.
 */
export const SettingsTab: React.FC = () => {
  const {
    params: { deployment, temperature, preamble, model },
    setParams,
  } = useParamsStore();
  const defaults = useSettingsDefaults();
  const { models } = useModels(deployment ?? '');
  const modelOptions = [
    {
      options: models.map((model) => ({
        label: model,
        value: model,
      })),
    },
  ];

  const reset = () => {
    setParams({
      ...defaults,
      tools: defaults.tools,
    });
  };

  return (
    <div className="flex flex-col gap-y-6 px-5 pb-10">
      <Dropdown
        className="w-full"
        label={STRINGS.model}
        kind="default"
        value={model}
        onChange={(model: string) => setParams({ model })}
        optionGroups={modelOptions}
      />
      <Slider
        className="w-full"
        label={STRINGS.temperature}
        min={0}
        max={1}
        step={0.1}
        value={temperature || 0}
        onChange={(temperature: number) => setParams({ temperature })}
        dataTestId="slider-temperature"
      />

      <InputLabel label={STRINGS.preamble}>
        <textarea
          value={preamble}
          placeholder={STRINGS.preambleExample}
          className={cn(
            'mt-2 w-full flex-1 resize-none p-3',
            'transition ease-in-out',
            'rounded-lg border',
            'bg-marble-1000',
            'border-marble-800 placeholder:text-volcanic-600 focus:border-mushroom-400',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-100',
            STYLE_LEVEL_TO_CLASSES.p
          )}
          rows={5}
          onChange={(e) => setParams({ preamble: e.target.value })}
          data-testid="input-preamble"
        />
      </InputLabel>

      <div className="flex w-full justify-end">
        <button type="button" onClick={reset}>
          <Text
            as="span"
            className="text-mushroom-300 transition ease-in-out hover:text-volcanic-100"
          >
            {STRINGS.reset}
          </Text>
        </button>
      </div>
    </div>
  );
};
