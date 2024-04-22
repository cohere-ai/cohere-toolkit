import IconButton from '@/components/IconButton';
import { Checkbox, Icon, Text } from '@/components/Shared';
import { useCitationsStore, useConversationStore, useSettingsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  isBulkActionMode: boolean;
  isSelectAllChecked: boolean;
  onSelectAllToggle: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBulkDeleteClick: VoidFunction;
  onSearchClick: VoidFunction;
};

export const ConversationListHeader: React.FC<Props> = ({
  isBulkActionMode,
  isSelectAllChecked,
  onSelectAllToggle,
  onBulkDeleteClick,
  onSearchClick,
}) => {
  const { setSettings, setIsConvListPanelOpen } = useSettingsStore();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();

  return (
    <header
      className={cn(
        'flex h-header w-full items-center justify-between border-b px-3 py-5',
        'border-marble-400',
        'overflow-hidden'
      )}
    >
      {isBulkActionMode ? (
        <div className="flex items-center gap-x-2">
          <Checkbox
            checked={isSelectAllChecked}
            indeterminate={!isSelectAllChecked}
            onChange={onSelectAllToggle}
            size="sm"
            theme="secondary"
            className="mx-2"
          />
          <IconButton iconName="trash" onClick={onBulkDeleteClick} />
        </div>
      ) : (
        <>
          <div className="flex items-center gap-x-2">
            <IconButton
              iconName="chevron-left"
              className="lg:hidden"
              onClick={() => setIsConvListPanelOpen(false)}
            />
            <IconButton
              iconName="side-panel"
              className="hidden lg:flex"
              onClick={() => setIsConvListPanelOpen(false)}
            />
            <span className="flex items-center gap-x-1">
              <Icon
                name="side-panel"
                className="flex h-8 w-8 items-center justify-center text-primary-500 lg:hidden"
                kind="outline"
              />
              <Text styleAs="p-lg">Chats</Text>
            </span>
          </div>
          <div className="flex items-center gap-x-3">
            <IconButton iconName="search" isDefaultOnHover={false} onClick={onSearchClick} />
            <IconButton
              href="/"
              shallow
              iconName="new-message"
              onClick={() => {
                resetConversation();
                resetCitations();
                setSettings({ isMobileConvListPanelOpen: false });
              }}
            />
          </div>
        </>
      )}
    </header>
  );
};
