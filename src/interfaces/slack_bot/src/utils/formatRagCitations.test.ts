import { describe, expect, test } from 'vitest';

import { formatRagCitations } from './formatRagCitations';

describe('formatRagCitations', () => {
  test('format RAG response into a list of bullet points, each as a slack link using the citation title + url', () => {
    const chatResponse = {
      response_id: 'aef874ef-bc61-45aa-9ade-4efac4fb12d3',
      conversation_id: '1705939582_599929-C05M1US4SSX',
      text: 'The following are some of the most popular programming languages in the world:\n\n- Python\n- TypeScript\n\nAre you looking to become a programmer?',
      generation_id: '12345678-30db-4d7d-a60a-d58cc7daa366',
      citations: [
        {
          start: 42,
          end: 67,
          text: 'Everything about Python',
          document_ids: ['elastic-search-slack-v1-0bdrwb_1', 'elastic-search-slack-v1-0bdrwb_3'],
        },
        {
          start: 70,
          end: 109,
          text: 'All about TypeScript',
          document_ids: ['elastic-search-slack-v1-0bdrwb_1', 'elastic-search-slack-v1-0bdrwb_0'],
        },
      ],
      documents: [
        {
          document_id: 'elastic-search-slack-v1-0bdrwb_1',
          snippet: 'Python 3.12 is fast!',
          title: 'Python',
          url: 'https://example.slack.com/archives/ask-programmers/p1699027927.191979?thread_ts=1699026229.534229',
          text: '',
          tool_name: '',
          fields: {},
        },
        {
          document_id: 'elastic-search-slack-v1-0bdrwb_3',
          snippet: 'Another popular language for frontend programming is TypeScript.',
          title: 'TypeScript',
          url: 'https://example.slack.com/archives/ask-programmers/p1698415906.928069?thread_ts=1698354798.078099',
          text: '',
          tool_name: '',
          fields: {},
        },
      ],
      is_finished: true,
      finish_reason: '',
      chat_history: [],
    };
    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(`
*Sources:*
- <https://example.slack.com/archives/ask-programmers/p1699027927.191979?thread_ts=1699026229.534229|Python>
- <https://example.slack.com/archives/ask-programmers/p1698415906.928069?thread_ts=1698354798.078099|TypeScript>`);
  });

  test('combine duplicate RAG response links into one citation and exclude documents that are not cited', () => {
    const chatResponse = {
      response_id: '00000000-0000-0000-0000-00000000001',
      conversation_id: '000000000_000000-000000012345',
      text: 'Here are some programming languages you could use to build a webapp. \n\n- Python\n\n- Ruby\n\n- TypeScript\n\nDo you want me to provide more information about any of these languages?',
      generation_id: '0000000-0000-0000-0000-12300000000',
      citations: [
        {
          start: 83,
          end: 96,
          text: 'TypeScript',
          document_ids: ['test-document-id-1'],
        },
        {
          start: 98,
          end: 114,
          text: 'Javascript',
          document_ids: ['test-document-id-1'],
        },
        {
          start: 118,
          end: 136,
          text: 'TypeScript and Javascript are both used with Node applications',
          document_ids: ['test-document-id-1'],
        },
      ],
      documents: [
        {
          document_id: 'test-document-id-1',
          snippet: 'All about TypeScript and Javascript',
          title: 'TypeScript and Javascript Programming',
          url: 'https://example.com/typescript-and-javascript',
          text: '',
          tool_name: '',
          fields: {},
        },
        {
          document_id: 'test-document-id-2',
          snippet: 'Python can be used for web APIs',
          title: 'About Python',
          url: 'https://example.com/python',
          text: '',
          tool_name: '',
          fields: {},
        },
        {
          document_id: 'test-document-id-3',
          snippet: 'Java',
          title: 'About Java',
          url: 'https://example.com/java',
          text: '',
          tool_name: '',
          fields: {},
        },
      ],
      finish_reason: '',
      is_finished: true,
      chat_history: [],
    };

    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(`
*Sources:*
- <https://example.com/typescript-and-javascript|TypeScript and Javascript Programming>`);
  });

  test('safely handles RAG response with not citation', () => {
    const chatResponse = {
      response_id: '00000000-0000-0000-0000-00000000001',
      conversation_id: '000000000_000000-000000012345',
      text: 'I could not find any information.',
      generation_id: '0000000-0000-0000-0000-12300000000',
      is_finished: true,
      finish_reason: '',
      chat_history: [],
    };

    const formattedCitations = formatRagCitations(chatResponse);
    expect(formattedCitations).toEqual(``);
  });
});
