import { useDebouncedEffect } from '@react-hookz/web';
import { matchSorter } from 'match-sorter';
import { useState } from 'react';

import { ConversationWithoutMessages } from '@/cohere-client';

/**
 * Hook in charge of searching conversations using:
 * 1. match-sorter for contains search for conversation name + description
 * 2. rerank endpoint for more advanced search
 * @param conversations from the API to filter
 */
export const useSearchConversations = (conversations: ConversationWithoutMessages[]) => {
  const [search, setSearch] = useState('');
  const [filteredConversations, setFilteredConversations] = useState<ConversationWithoutMessages[]>(
    []
  );

  useDebouncedEffect(
    async () => {
      if (conversations.length === 0) return;
      if (search.trim().length === 0) {
        setFilteredConversations(conversations);
        return;
      }
      const matchSortedConversations = matchSorter(conversations, search, {
        keys: [
          { threshold: matchSorter.rankings.CONTAINS, key: 'name' },
          { threshold: matchSorter.rankings.CONTAINS, key: 'description' },
        ],
      });
      return setFilteredConversations(matchSortedConversations);
    },
    [search, conversations],
    500
  );

  return { search, setSearch, searchResults: filteredConversations };
};
