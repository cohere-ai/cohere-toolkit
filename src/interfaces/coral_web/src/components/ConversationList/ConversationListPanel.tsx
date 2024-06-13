import { Transition } from '@headlessui/react';
import { useClickOutside } from '@react-hookz/web';
import React, { useEffect, useMemo, useRef, useState } from 'react';

import { ConversationWithoutMessages as Conversation } from '@/cohere-client';
import { ConversationListHeader } from '@/components/ConversationList/ConversationListHeader';
import { ConversationListLoading } from '@/components/ConversationList/ConversationListLoading';
import { ConversationListPanelGroup } from '@/components/ConversationList/ConversationListPanelGroup';
import { Icon, Input, Text } from '@/components/Shared';
import { getIsTouchDevice } from '@/hooks/breakpoint';
import { useConversations } from '@/hooks/conversation';
import { useSearchConversations } from '@/hooks/search';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

const sortByDate = (a: Conversation, b: Conversation) => {
  return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
};

type Props = {
  className?: string;
};
export const ConversationListPanel: React.FC<Props> = ({ className }) => {
  const panelRef = useRef(null);
  const { data, isLoading: isConversationsLoading, isError } = useConversations();
  const conversations: Conversation[] = data ?? [];

  const {
    settings: { isConvListPanelOpen },
  } = useSettingsStore();

  const [checkedConversations, setCheckedConversations] = useState<Set<string>>(new Set());
  const [showSearch, setShowSearch] = useState(false);
  const { search, setSearch, searchResults } = useSearchConversations(conversations);
  const hasSearchQuery = search.length > 0;
  const hasSearchResults = searchResults.length > 0;
  const hasConversations = conversations.length > 0;
  const allConversationsChecked = checkedConversations.size === conversations.length;

  const displayedConversations = useMemo<Conversation[]>(() => {
    return search ? searchResults : conversations.sort(sortByDate);
  }, [searchResults, conversations, search]);

  useEffect(() => {
    if (!isConvListPanelOpen && showSearch) {
      setShowSearch(false);
      setSearch('');
    }
  }, [isConvListPanelOpen, showSearch]);

  useClickOutside(panelRef, () => {
    if (showSearch) {
      setShowSearch(false);
      setSearch('');
    }
  });

  const handleSearchToggle = () => {
    const newShowSearch = !showSearch;
    if (!newShowSearch) {
      setSearch('');
    }
    setShowSearch(newShowSearch);
  };

  const handleCheckConversationToggle = (id: string) => {
    const newCheckedConversations = new Set(checkedConversations);
    if (!newCheckedConversations.delete(id)) {
      newCheckedConversations.add(id);
    }
    setCheckedConversations(newCheckedConversations);
  };

  const handleCheckAllToggle = () => {
    if (allConversationsChecked) {
      setCheckedConversations(new Set());
    } else {
      setCheckedConversations(new Set(displayedConversations.map((c) => c.id ?? '')));
    }
  };

  let content;
  if (isConversationsLoading) {
    content = <ConversationListLoading />;
  } else if (isError) {
    content = (
      <span className="my-auto flex flex-col items-center gap-2 text-center">
        <Icon name="warning" />
        <Text>Unable to load conversations.</Text>
      </span>
    );
  } else if (hasSearchQuery && !hasSearchResults) {
    content = (
      <Text as="span" className="line-clamp-3">
        No results found for &quot;{search}&quot;.
      </Text>
    );
  } else if (!hasConversations) {
    content = (
      <span className="flex h-full w-full items-center justify-center text-volcanic-600">
        <Text>It&apos;s quiet here... for now</Text>
      </span>
    );
  } else {
    content = (
      <ConversationListPanelGroup
        conversations={displayedConversations}
        showWeekHeadings={!hasSearchQuery}
        checkedConversations={checkedConversations}
        onCheckConversation={handleCheckConversationToggle}
      />
    );
  }

  return (
    <Transition.Child
      ref={panelRef}
      as="nav"
      enterFrom="lg:opacity-0"
      enterTo="lg:opacity-100"
      leaveFrom="lg:opacity-100"
      leaveTo="lg:opacity-0"
      className={cn(
        'transition-opacity ease-in-out lg:duration-500',
        'flex h-full w-full flex-grow flex-col',
        className
      )}
    >
      <ConversationListHeader
        isBulkActionMode={checkedConversations.size > 0}
        isSelectAllChecked={allConversationsChecked}
        onSelectAllToggle={handleCheckAllToggle}
        onBulkDeleteClick={() => {}}
        onSearchClick={handleSearchToggle}
      />

      <Transition
        show={showSearch}
        enterFrom="opacity-0 h-0 mt-0"
        enterTo="opacity-100 h-12 mt-5"
        leaveFrom="opacity-100 h-12 mt-5"
        leaveTo="opacity-0 h-0 mt-0"
        as="div"
        className="z-menu px-4 duration-300 ease-in-out"
      >
        <Input
          placeholder="Search"
          theme="secondary"
          actionType="search"
          kind="default"
          size="sm"
          maxLength={40}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onClear={() => setSearch('')}
        />
      </Transition>

      <section
        className={cn(
          'relative flex h-0 flex-grow flex-col overflow-y-auto',
          'px-3 pb-4 pt-3 md:pb-8',
          { 'hide-scrollbar pr-0.5': !getIsTouchDevice() }
        )}
      >
        {content}
      </section>
    </Transition.Child>
  );
};

export default ConversationListPanel;
