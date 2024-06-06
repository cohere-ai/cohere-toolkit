import { ALERTS } from 'src/constants';

import { Document, NonStreamedChatResponse } from '../cohere-client';

export const formatRagCitations = (
  chatResponse: NonStreamedChatResponse,
  prefix = ALERTS.RAG_SOURCES_PREFIX,
): string => {
  // find set of documents that are actually cited
  const sources = new Set((chatResponse.citations ?? []).map((c) => c.document_ids).flat());

  // dedupe citations by url
  const citations = Object.values(
    (chatResponse.documents ?? [])
      .filter((d) => sources.has(d.document_id))
      .reduce((acc: { [key: string]: Document }, d) => {
        if (d.url) {
          acc[d.url] = d;
        }
        return acc;
      }, {}),
  );

  // safely handle when no citations are found
  if (citations.length === 0) {
    return '';
  }

  // basic formatting for slack (bullet point with link)
  const formattedCitations = citations
    .map((d) => (d.title ? `- <${d.url}|${d.title}>` : `- ${d.url}`))
    .join('\n');
  return `\n${prefix}\n${formattedCitations}`;
};
