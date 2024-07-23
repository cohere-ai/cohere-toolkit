'use client';

import {
  Dropdown,
  InputLabel,
  STYLE_LEVEL_TO_CLASSES,
  Slider,
  Text,
  Textarea,
} from '@/components/Shared';
import { useModels } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
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
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;
  const { models } = useModels(deployment ?? '');
  const modelOptions = models.map((model) => ({
    label: model,
    value: model,
  }));

  const reset = () => {
    setParams({
      ...defaults,
      tools: defaults.tools,
    });
  };

  if (isLangchainModeOn) {
    return (
      <div className="flex items-center justify-center px-5">
        <Text styleAs="p-lg" className="select-none text-center text-volcanic-100">
          Currently settings are disabled with experimental Langchain multihop
        </Text>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-y-6 px-5 pb-10">
      <Dropdown
        className="w-full"
        label="Model"
        value={model}
        placeholder="Select a model"
        onChange={(model: string) => setParams({ model })}
        options={modelOptions}
      />
      <Slider
        className="w-full"
        label="Temperature"
        min={0}
        max={1}
        step={0.1}
        value={temperature || 0}
        onChange={(temperature: number) => setParams({ temperature })}
        dataTestId="slider-temperature"
      />

      <InputLabel label="Preamble">
        <Textarea
          value={preamble}
          placeholder="e.g. You are Coral, a large language model trained to have polite, helpful, inclusive conversations with people."
          rows={5}
          onChange={(e) => setParams({ preamble: e.target.value })}
        />
      </InputLabel>

      <div className="flex w-full justify-end">
        <button type="button" onClick={reset}>
          <Text
            as="span"
            className="text-mushroom-300 transition ease-in-out hover:text-volcanic-100"
          >
            Reset
          </Text>
        </button>
      </div>
    </div>
  );
};
