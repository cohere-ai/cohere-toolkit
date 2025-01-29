import { Switch, Text } from '@/components/UI';
import { useSettingsStore } from '@/stores';

export const ShowStepsToggle = () => {
  const { showSteps, setShowSteps } = useSettingsStore();

  const handleSwitchShowSteps = (checked: boolean) => {
    setShowSteps(checked);
  };

  return (
    <section className="mb-4 flex gap-6">
      <Text styleAs="label" className="font-medium">
        Show thinking steps
      </Text>
      <Switch
        checked={showSteps}
        onChange={(checked: boolean) => handleSwitchShowSteps(checked)}
        showCheckedState
      />
    </section>
  );
};
