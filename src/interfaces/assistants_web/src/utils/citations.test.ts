import { describe, expect, test } from 'vitest';

import { Citation } from '@/cohere-client';
import { fixCitationsLeadingMarkdown, replaceTextWithCitations } from '@/utils/citations';

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

  test('should avoid to break markdown images', () => {
    const citations: Citation[] = [
      {
        start: 0,
        end: 26,
        text: '! [test](https://test.com)',
        document_ids: ['12345'],
      },
    ];
    const text = '![test](https://test.com)';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe(
      ':cite[![test](https://test.com)]{generationId="12345" start="0" end="26"}'
    );
  });

  test('should handle extra space when fixing markdown images', () => {
    const citations: Citation[] = [
      {
        start: 5,
        end: 31,
        text: '! [test](https://test.com)',
        document_ids: ['12345'],
      },
      {
        start: 32,
        end: 39,
        text: 'Kadabra',
        document_ids: ['44444'],
      },
    ];
    const text = 'Abra ![test](https://test.com) Kadabra';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe(
      'Abra :cite[![test](https://test.com)]{generationId="12345" start="5" end="31"} :cite[Kadabra]{generationId="12345" start="32" end="39"}'
    );
  });

  test('should allow citations as markdown elements', () => {
    const citations: Citation[] = [
      {
        start: 10,
        end: 18,
        text: '**test**',
        document_ids: ['12345'],
      },
    ];
    const text = 'This is a **test** text';
    const generationId = '12345';
    const result = replaceTextWithCitations(text, citations, generationId);
    expect(result).toBe('This is a :cite[**test**]{generationId="12345" start="10" end="18"} text');
  });
});

describe('fixCitationsLeadingMarkdown', () => {
  test('should fix leading markdown citations breaking markdown', () => {
    const citations: Citation[] = [
      {
        text: '`ENVIRONMENT DIVISION',
        start: 4,
        end: 25,
        document_ids: ['111111'],
      },
      {
        text: 'after the',
        start: 46,
        end: 55,
        document_ids: ['111111'],
      },
      {
        text: '`IDENTIFICATION DIVISION',
        start: 56,
        end: 80,
        document_ids: ['111111'],
      },
      {
        text: '`CONFIGURATION SECTION',
        start: 87,
        end: 109,
        document_ids: ['111111'],
      },
      {
        text: '`SPECIAL-NAMES',
        start: 115,
        end: 129,
        document_ids: ['111111'],
      },
      {
        text: 'within the',
        start: 150,
        end: 160,
        document_ids: ['111111'],
      },
    ];
    const text =
      'The `ENVIRONMENT DIVISION` should be included after the `IDENTIFICATION DIVISION`. The `CONFIGURATION SECTION` and `SPECIAL-NAMES` should be included within the `ENVIRONMENT DIVISION`.';
    const result = fixCitationsLeadingMarkdown(citations, text);

    expect(result).toStrictEqual([
      {
        text: '`ENVIRONMENT DIVISION`',
        start: 4,
        end: 26,
        document_ids: ['111111'],
      },
      {
        text: 'after the',
        start: 46,
        end: 55,
        document_ids: ['111111'],
      },
      {
        text: '`IDENTIFICATION DIVISION`',
        start: 56,
        end: 81,
        document_ids: ['111111'],
      },
      {
        text: '`CONFIGURATION SECTION`',
        start: 87,
        end: 110,
        document_ids: ['111111'],
      },
      {
        text: '`SPECIAL-NAMES`',
        start: 115,
        end: 130,
        document_ids: ['111111'],
      },
      {
        text: 'within the',
        start: 150,
        end: 160,
        document_ids: ['111111'],
      },
    ]);
  });

  test('should push markdown downloable links to the end', () => {
    const citations: Citation[] = [
      {
        text: '[link](https://www.google.com)',
        start: 10,
        end: 39,
        document_ids: ['111111'],
      },
      {
        text: "[link]('.file_path.csv')",
        start: 64,
        end: 87,
        document_ids: ['111111'],
      },
    ];
    const text =
      "This is a [link](https://www.google.com) and this is downloable [link]('file_path.csv')";
    const result = fixCitationsLeadingMarkdown(citations, text);
    expect(result).toStrictEqual([
      {
        text: '[link](https://www.google.com)',
        end: 39,
        start: 88,
        document_ids: ['111111'],
      },
      {
        text: "[link]('.file_path.csv')",
        end: 87,
        start: 88,
        document_ids: ['111111'],
      },
    ]);
  });
});
