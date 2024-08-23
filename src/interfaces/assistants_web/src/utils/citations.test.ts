import { describe, expect, test } from 'vitest';

import { Citation } from '@/cohere-client';
import {
  CODE_BLOCK_REGEX_EXP,
  IFRAME_REGEX_EXP,
  fixInlineCitationsForMarkdown,
  isReferenceBetweenSpecialTags,
  replaceTextWithCitations,
} from '@/utils';

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

  test('should fix citations position for to get the correct markdown', () => {
    const citations = [
      {
        text: '(fn',
        start: 71,
        end: 74,
        document_ids: ['12345'],
      },
      {
        text: 'delay',
        start: 76,
        end: 81,
        document_ids: ['12345'],
      },
      {
        text: 'let debounceTimer',
        start: 86,
        end: 103,
        document_ids: ['12345'],
      },
      {
        text: 'return function',
        start: 107,
        end: 122,
        document_ids: ['12345'],
      },
      {
        text: 'args',
        start: 126,
        end: 130,
        document_ids: ['12345'],
      },
      {
        text: 'clearTimeout',
        start: 135,
        end: 147,
        document_ids: ['12345'],
      },
      {
        text: '(debounceTimer',
        start: 147,
        end: 161,
        document_ids: ['12345'],
      },
      {
        text: 'debounceTimer = setTimeout',
        start: 165,
        end: 191,
        document_ids: ['12345'],
      },
      {
        text: 'fn.apply(this, args',
        start: 201,
        end: 220,
        document_ids: ['12345'],
      },
      {
        text: 'delay',
        start: 227,
        end: 232,
        document_ids: ['12345'],
      },
      {
        text: 'code is only executed once per user input',
        start: 285,
        end: 326,
        document_ids: ['12345'],
      },
      {
        text: 'takes two parameters',
        start: 331,
        end: 351,
        document_ids: ['12345'],
      },
      {
        text: 'the function to be debounced',
        start: 353,
        end: 381,
        document_ids: ['12345'],
      },
      {
        text: 'the delay in milliseconds',
        start: 386,
        end: 411,
        document_ids: ['12345'],
      },
    ];
    const text =
      "Here's a JavaScript debounce function: ```javascript function debounce(fn, delay) {   let debounceTimer;    return function(...args) {     clearTimeout(debounceTimer);     debounceTimer = setTimeout(() => {       fn.apply(this, args);     }, delay);   }; } ```  The debounce function ensures that the code is only executed once per user input. It takes two parameters: the function to be debounced and the delay in milliseconds.";
    const result = fixInlineCitationsForMarkdown(citations, text);
    expect(result).toStrictEqual([
      {
        text: '(fn',
        start: 71,
        end: 74,
        document_ids: ['12345'],
      },
      {
        text: 'delay',
        start: 76,
        end: 81,
        document_ids: ['12345'],
      },
      {
        text: 'let debounceTimer',
        start: 86,
        end: 103,
        document_ids: ['12345'],
      },
      {
        text: 'return function',
        start: 107,
        end: 122,
        document_ids: ['12345'],
      },
      {
        text: 'args',
        start: 126,
        end: 130,
        document_ids: ['12345'],
      },
      {
        text: 'clearTimeout',
        start: 135,
        end: 147,
        document_ids: ['12345'],
      },
      {
        text: '(debounceTimer',
        start: 147,
        end: 161,
        document_ids: ['12345'],
      },
      {
        text: 'debounceTimer = setTimeout',
        start: 165,
        end: 191,
        document_ids: ['12345'],
      },
      {
        text: 'fn.apply(this, args',
        start: 201,
        end: 220,
        document_ids: ['12345'],
      },
      {
        text: 'delay',
        start: 227,
        end: 232,
        document_ids: ['12345'],
      },
      {
        text: 'code is only executed once per user input',
        start: 301,
        end: 342,
        document_ids: ['12345'],
      },
      {
        text: 'takes two parameters',
        start: 347,
        end: 367,
        document_ids: ['12345'],
      },
      {
        text: 'the function to be debounced',
        start: 369,
        end: 397,
        document_ids: ['12345'],
      },
      {
        text: 'the delay in milliseconds',
        start: 402,
        end: 427,
        document_ids: ['12345'],
      },
    ]);
  });
});

describe('isReferenceBetweenSpecialTags', () => {
  test('should return true if the citation is between <iframe> tags', () => {
    const text = '<iframe> This is a citation </iframe>';
    const citation: Citation = {
      start: 19,
      end: 27,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(IFRAME_REGEX_EXP, text, citation.start);
    expect(result).toBe(true);
  });
  test('should return false if the citation is not between <iframe> tags', () => {
    const text = 'This is a citation <iframe> another test citaiton </iframe>';
    const citation: Citation = {
      start: 10,
      end: 18,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(IFRAME_REGEX_EXP, text, citation.start);
    expect(result).toBe(false);
  });
  test('should return true if the citation is between ``` tags', () => {
    const text = '``` This is a citation ```';
    const citation: Citation = {
      start: 14,
      end: 22,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, text, citation.start);
    expect(result).toBe(true);
  });
  test('should return false if the citation is not between ``` tags', () => {
    const text = '``` This is a citation ``` another test citaiton';
    const citation: Citation = {
      start: 40,
      end: 48,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, text, citation.start);
    expect(result).toBe(false);
  });
  test('should be able to check if there are more than one match', () => {
    const text = '``` This is a citation ``` another test citaiton ``` final citation ``` ';
    const citation: Citation = {
      start: 59,
      end: 67,
      text: 'citation',
      document_ids: ['12345'],
    };
    const result = isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, text, citation.start);
    expect(result).toBe(true);
  });
});
