import { Switch, Text } from '@/components/UI';
import { useSettingsStore } from '@/stores';

export const ShowCitationsToggle = () => {
  const { showCitations, setShowCitations } = useSettingsStore();

  const handleSwitchShowCitations = (checked: boolean) => {
    setShowCitations(checked);
  };

  return (
    <section className="mb-4 flex gap-6">
      <Text styleAs="label" className="font-medium">
        Show citations
      </Text>
      <Switch
        checked={showCitations}
        onChange={(checked: boolean) => handleSwitchShowCitations(checked)}
        showCheckedState
      />
    </section>
  );
};
