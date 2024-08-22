import { describe, expect, test } from 'vitest';

import { Citation } from '@/cohere-client';
import {
  fixInlineCitationsForMarkdown,
  isReferenceBetweenSpecialTags,
  replaceTextWithCitations,
} from '@/utils/citations';

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

describe('fixInlineCitationsForMarkdown', () => {
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
    const result = fixInlineCitationsForMarkdown(citations, text);

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
    const result = fixInlineCitationsForMarkdown(citations, text);
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

  test('should remove extra blank space on markdown images', () => {
    const citations: Citation[] = [
      {
        start: 0,
        end: 25,
        text: '! [test](https://test.com)',
        document_ids: ['12345'],
      },
      {
        start: 26,
        end: 33,
        text: 'Kadabra',
        document_ids: ['44444'],
      },
    ];
    const text = '![test](https://test.com) Kadabra';
    const result = fixInlineCitationsForMarkdown(citations, text);
    expect(result).toStrictEqual([
      {
        start: 34,
        end: 25,
        text: '![test](https://test.com)',
        document_ids: ['12345'],
      },
      {
        start: 25,
        end: 32,
        text: 'Kadabra',
        document_ids: ['44444'],
      },
    ]);
  });
});

describe('isReferenceBetweenSpecialTags', () => {
  test('should return true if the citation is between <iframe> tags', () => {
    const matchRegex = /<iframe>.*<\/iframe>/;
    const text = '<iframe> This is a citation </iframe>';
    const citation: Citation = {
      start: 19,
      end: 27,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(matchRegex, text, citation.start);
    expect(result).toBe(true);
  });
  test('should return false if the citation is not between <iframe> tags', () => {
    const matchRegex = /<iframe>.*<\/iframe>/;
    const text = 'This is a citation <iframe> another test citaiton </iframe>';
    const citation: Citation = {
      start: 10,
      end: 18,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(matchRegex, text, citation.start);
    expect(result).toBe(false);
  });
  test('should return true if the citation is between ``` tags', () => {
    const matchRegex = /```[\s\S]*?```/g;
    const text = '``` This is a citation ```';
    const citation: Citation = {
      start: 14,
      end: 22,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(matchRegex, text, citation.start);
    expect(result).toBe(true);
  });
  test('should return false if the citation is not between ``` tags', () => {
    const matchRegex = /```[\s\S]*?```/g;
    const text = '``` This is a citation ``` another test citaiton';
    const citation: Citation = {
      start: 40,
      end: 48,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(matchRegex, text, citation.start);
    expect(result).toBe(false);
  });
});
