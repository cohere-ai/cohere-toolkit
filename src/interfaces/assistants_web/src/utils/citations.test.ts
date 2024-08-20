import { describe, expect, test } from 'vitest';

import { Citation } from '@/cohere-client';
import { replaceTextWithCitations } from '@/utils/citations';

describe('replaceTextWithCitations', () => {
  test('should replace text with citations', () => {
    const citations: Citation[] = [
      {
        start: 0,
        end: 4,
        text: 'test',
        document_ids: ['12345'],
      },
    ];
    const text = 'This is a test text';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe(':cite[test]{generationId="12345" start="0" end="4"} is a test text');
  });

  test('should return text if citations are empty', () => {
    const citations: Citation[] = [];
    const text = 'This is a test text';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe(text);
  });

  test('should avoid add citations inside of iframes', () => {
    const citations: Citation[] = [
      {
        start: 14,
        end: 21,
        text: 'Kadabra',
        document_ids: ['12345'],
      },
    ];
    const text = 'Abra <iframe> Kadabra </iframe> Alakazam';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe(
      'From: :cite[Reference #1]{generationId="12345" start="14" end="21"}\nAbra <iframe> Kadabra </iframe> Alakazam'
    );
  });
});
