import { useMemo, useState } from 'react';

import { ManagedTool } from '@/cohere-client';
import { Tag } from '@/components/Conversation/Composer/DataSourceMenu';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';
import { useListFiles } from '@/hooks/files';
import { useListTools } from '@/hooks/tools';
import { useConversationStore } from '@/stores';
import { formatFileSize } from '@/utils';

/**
 * @description Hook that contains all the logic for filtering and displaying tags
 * for data sources.
 */
export const useDataSourceTags = ({ requiredTools }: { requiredTools?: string[] }) => {
  const [tagQuery, setTagQuery] = useState<string>('');
  const {
    conversation: { id },
  } = useConversationStore();
  const query = tagQuery.replace('@', '');
  const { data: tools = [] } = useListTools();
  const { data: files } = useListFiles(id);
  const onlyRequiredTools = useMemo(() => {
    const availableTools = tools.filter((t) => t.is_visible && t.is_available);
    if (!requiredTools) {
      return availableTools;
    }

    return requiredTools
      .map((rt) => availableTools.find((t) => t.name === rt))
      .filter((t) => !!t) as ManagedTool[];
  }, [tools, requiredTools]);

  const filteredFileIdTags: Tag[] = useMemo(
    () =>
      (files ?? [])
        .filter((file) => {
          return file.file_name.toLowerCase().includes(query.toLowerCase());
        })
        .map(({ id, file_name, file_size = 0 }) => ({
          id,
          name: file_name,
          metadata: formatFileSize(file_size),
          getValue: () => id,
        })),
    [files, query]
  );

  const allToolTags: Tag[] = useMemo(() => {
    const allTools = [];
    for (const t of onlyRequiredTools) {
      allTools.push({
        id: t.name ?? '',
        name: t.display_name ?? t.name ?? '',
        description: t.description ?? '',
        icon: TOOL_ID_TO_DISPLAY_INFO[t.name ?? '']?.icon ?? TOOL_FALLBACK_ICON,
        getValue: () => t,
      });
    }
    return allTools;
  }, [onlyRequiredTools]);
  const filteredToolTags: Tag[] = useMemo(
    () =>
      allToolTags.filter(
        (tag) =>
          tag.id.toLowerCase().includes(query.toLowerCase()) ||
          tag.name.toLowerCase().includes(query.toLowerCase())
      ),
    [allToolTags, query]
  );

  // if user types @ at the current input cursor position, return the @ and the string that follows
  const getTagQuery = (value: string, cursorPosition: number): string => {
    // Find the nearest space to the left of the cursor position
    const spaceIndex = value.lastIndexOf(' ', cursorPosition);

    // Determine the starting index based on the nearest space
    const startIndex = spaceIndex !== -1 ? spaceIndex + 1 : 0;

    // Match the first word of the string if it starts with "@"
    const regexPattern = /^@(\S*)/;
    const match = value.substring(startIndex).match(regexPattern);
    if (match) {
      return match[0];
    }
    return '';
  };

  return {
    suggestedTags: {
      fileIds: filteredFileIdTags,
      tools: filteredToolTags,
    },
    totalTags: {
      fileIds: files?.length ?? 0,
    },
    tagQuery,
    setTagQuery,
    getTagQuery,
  };
};
