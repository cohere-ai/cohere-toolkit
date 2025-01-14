'use client';

import { ComponentPropsWithoutRef, FC, useCallback } from 'react';
import { ExtraProps } from 'react-markdown';

import { StructuredTable } from '@/components/Markdown/directives/table-tools';
import { Icon, Text } from '@/components/UI';
import { useNotify } from '@/hooks';
import { useConversationStore } from '@/stores';
import { cn, downloadFile, structuredTableToXSV } from '@/utils';

const FALLBACK_FILE_NAME = 'cohere-table';

type ElementProps = {
  hProperties: {
    structuredTable: StructuredTable;
  };
};

/**
 * A React component that wraps a table generated from Markdown and adds functionality related to the data in the table
 * (such as downloading the table as a CSV)
 *
 * Relies on the `renderTableTools` plugin for making the table data available in a structure format
 *
 * How to test: Every Markdown table gets converted to a DataTable. In the chat app, try the following query:
 * "Create a table with 2 columns: (1) Cuisine; (2) One popular dish from that cuisine"
 */
export const DataTable: FC<ComponentPropsWithoutRef<'table'> & ExtraProps> = ({
  children,
  node,
}) => {
  const data = node?.data as ElementProps | undefined;
  const structuredTable = data?.hProperties?.structuredTable;

  const {
    conversation: { name: conversationName },
  } = useConversationStore();
  const { error } = useNotify();

  const downloadAsCSV = useCallback(() => {
    const csv = structuredTableToXSV(structuredTable!, ',');
    if (csv === null) {
      error('Unable to download table as CSV.');
      return;
    }

    const fileName = conversationName?.trim()?.replaceAll(' ', '-') || FALLBACK_FILE_NAME;
    downloadFile(`${fileName}.csv`, [csv]);
  }, [structuredTable]);

  return (
    <div className="py-2">
      <table className="my-0">{children}</table>
      {structuredTable && (
        <button
          data-testid="button-md-table-download-csv"
          className={cn(
            'mt-2 flex items-center gap-x-1 rounded p-1',
            'text-mushroom-400 transition ease-in-out hover:bg-mushroom-900 hover:text-mushroom-300'
          )}
          onClick={downloadAsCSV}
        >
          <Icon name="sparkle" kind="outline" />
          <Text styleAs="p-sm">Download as CSV</Text>
        </button>
      )}
    </div>
  );
};
