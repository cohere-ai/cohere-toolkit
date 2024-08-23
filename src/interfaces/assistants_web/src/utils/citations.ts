import { Citation } from '@/cohere-client';

/**
 * @description Helper function to temporarily ensure markdown image syntax provided by the model is correct.
 * This is a temporary fix as the current model is consistently returning incorrect markdown image syntax.
 * @param text - message text or citation text
 */
export const fixMarkdownImagesInText = (text: string) => {
  return text.replace('! [', '![');
};

const formatter = new Intl.ListFormat('en', { style: 'long', type: 'conjunction' });

export const IFRAME_REGEX_EXP = /<iframe.*<\/iframe>/;
export const CODE_BLOCK_REGEX_EXP = /```[\s\S]*?```/;
export const LATEX_REGEX_EXP = /\$\$([\s\S]*?)\$\$/;

/**
 * Escape special regex characters in a string
 * @param str
 * @returns Escaped string
 */
const escapeRegex = (str: string) => str.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
/**
 * Returns true if the string has an odd number of occurrences of the sequence or sequences
 * @param str - The string to check
 * @param sequence - A string or array of strings to check for odd occurrences
 * @returns boolean
 */
const hasOddOccurrences = (str: string, sequence: string | string[]): boolean => {
  const sequences = Array.isArray(sequence) ? sequence : [sequence];

  // Escape special regex characters in the sequences
  const escapedSequences = sequences.map((seq) => seq.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  // Create the regex pattern
  const regexPattern = escapedSequences
    .map((seq) => `^(?:[^${seq}]*${seq}){1}(?:[^${seq}]*${seq}[^${seq}]*${seq})*[^${seq}]*$`)
    .join('|');

  const regex = new RegExp(regexPattern);

  return regex.test(str);
};
/**
 * Based on the citation, find the closest match in the text
 * @param citation
 * @param matches
 * @returns Best match or first match if no better match is found
 */
const getClosestMatch = (citation: Citation, matches: RegExpMatchArray[]) => {
  const initalStart = citation.start;
  const initalEnd = citation.end;
  let bestMatch = matches[0];
  let cumulativeDelta = Number.MAX_SAFE_INTEGER;

  for (const match of matches) {
    if (!match.indices) {
      continue;
    }

    const [start, end] = match.indices[0];
    const diff = Math.abs(start - initalStart) + Math.abs(end - initalEnd);
    if (diff <= cumulativeDelta) {
      cumulativeDelta = diff;
      bestMatch = match;
    }
  }

  return bestMatch;
};

const tryToFixCitationsInCodeBlock = (citations: Citation[], originalText: string) => {
  const citationsCopy = structuredClone(citations);

  for (const citation of citationsCopy) {
    // since we are pushing out the citations out of the special blocks, we need to check if the citation is inside one of them
    if (
      isReferenceBetweenSpecialTags(IFRAME_REGEX_EXP, originalText, citation.start) ||
      isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, originalText, citation.start) ||
      isReferenceBetweenSpecialTags(LATEX_REGEX_EXP, originalText, citation.start)
    ) {
      continue;
    }

    try {
      const regex = new RegExp(escapeRegex(citation.text), 'dg');
      const matches = Array.from(originalText.matchAll(regex)).filter(
        (match) =>
          !isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, originalText, match.index) ||
          !isReferenceBetweenSpecialTags(LATEX_REGEX_EXP, originalText, match.index)
      );

      const bestMatch = getClosestMatch(citation, matches);
      if (bestMatch.indices) {
        const [start, end] = bestMatch.indices[0];
        citation.start = start;
        citation.end = end;
      }
    } catch (e) {
      console.error('error updating citation', citation, e);
    }
  }

  return citationsCopy;
};

export const fixInlineCitationsForMarkdown = (citations: Citation[], originalText: string) => {
  let citationsCopy = structuredClone(citations);
  const markdownFixList = ['`', '*', '**', '$', '$$', [`{`, `}`]];
  const matchDownloableMarkdownLink = /\[.*\]\(.*/;
  let carryOver = 0;

  // try to fix citations start and end indexes in case they are a code block on the text
  if (originalText.match(CODE_BLOCK_REGEX_EXP) || originalText.match(LATEX_REGEX_EXP)) {
    citationsCopy = tryToFixCitationsInCodeBlock(citationsCopy, originalText);
  }

  for (let citation of citationsCopy) {
    if (carryOver) {
      citation.start += carryOver;
      citation.end += carryOver;
    }

    for (const markdown of markdownFixList) {
      /**
       * fix citations breaking markdown.
       * e.g.:
       * originalText: `Abra envolves into **Kadabra**`
       * citation = { start: 44, end: 53, text: '**Kadabra', document_ids: ['12345'] }
       * Explanation: it will render as `Abra envolves into cite[**Kadabra]{generationId="12345" start="44" end="53"}**`
       * breaking the markdown layout. This fix will ensure the citation is rendered as `Abra envolves into cite[**Kadabra**]{generationId="12345" start="44" end="53"}`
       */
      if (
        hasOddOccurrences(citation.text, markdown) && // it has an odd number of markdown characters
        !isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, originalText, citation.start) && // is not in a code block
        !isReferenceBetweenSpecialTags(LATEX_REGEX_EXP, originalText, citation.start) // is not in a code block
      ) {
        const endMarkdown = typeof markdown === 'string' ? markdown : markdown[1];
        const canWeIncludeNextCharacterInTheCitation =
          originalText.charAt(citation.end) === endMarkdown; // the next character the markdown character
        if (canWeIncludeNextCharacterInTheCitation) {
          citation.end += markdown.length;
          citation.text = citation.text + endMarkdown;
        }
      }

      const isCitationInsideOfCodeBlock = isReferenceBetweenSpecialTags(
        CODE_BLOCK_REGEX_EXP,
        originalText,
        citation.start
      );
      const isOutOfBonds = citation.start >= originalText.length + 1; // if the citation is outside of the text

      if (citation.text.startsWith(' [') && !isOutOfBonds && !isCitationInsideOfCodeBlock) {
        citation.text = citation.text.slice(1);
        carryOver -= 1;
      }

      if (citation.text.startsWith('! [') && !isOutOfBonds && !isCitationInsideOfCodeBlock) {
        citation.text = '![' + citation.text.slice(3);
        carryOver -= 1;
      }

      if (citation.text.match(matchDownloableMarkdownLink)) {
        // push the citation to the end so it shows up as a 'Other references'
        citation.start = originalText.length + 1;
      }
    }
  }

  return citationsCopy;
};

/**
 * Replace text string with citations following the format:
 *  :cite[<text>]{generationId="<generationId>" start="<startIndex>" end"<endIndex>"}
 * @param text
 * @param citations
 * @param generationId
 * @returns text with citations
 */
export const replaceTextWithCitations = (
  text: string,
  citations: Citation[],
  generationId: string
) => {
  if (!citations.length || !generationId) return text;

  let notFoundReferences: string[] = [];
  let iFrameReferences: string[] = [];
  let codeBlockReferences: string[] = [];
  let replacedText = text;
  let lengthDifference = 0; // Track the cumulative length difference
  let carryOver = 0;

  citations
    .filter((citation) => citation.document_ids.length)
    .forEach(({ start = 0, end = 0, text: citationText }, index) => {
      let citeStart = start + lengthDifference + carryOver;
      let citeEnd = end + lengthDifference + carryOver;

      // if citeStart is higher than the length of the text, add it to the bottom of the text as "Reference #n"
      if (start >= text.length) {
        const ref = `Reference #${index + 1}`;
        notFoundReferences.push(
          `:cite[${ref}]{generationId="${generationId}" start="${start}" end="${end}"}`
        );
        return;
      }

      if (isReferenceBetweenSpecialTags(IFRAME_REGEX_EXP, replacedText, citeStart)) {
        const ref = `Reference #${iFrameReferences.length + 1}`;
        iFrameReferences.push(
          `:cite[${ref}]{generationId="${generationId}" start="${start}" end="${end}"}`
        );
        iFrameReferences.push();
        return;
      }

      if (
        isReferenceBetweenSpecialTags(CODE_BLOCK_REGEX_EXP, replacedText, citeStart) ||
        isReferenceBetweenSpecialTags(LATEX_REGEX_EXP, replacedText, citeStart)
      ) {
        const ref = `Reference #${codeBlockReferences.length + 1}`;
        codeBlockReferences.push(
          `:cite[${ref}]{generationId="${generationId}" start="${start}" end="${end}"}`
        );
        codeBlockReferences.push();
        return;
      }

      // Encode the citationText in case there are any weird characters or unclosed brackets that will
      // interfere with parsing the markdown. However, let markdown images through so they may be properly
      // rendered.
      const isMarkdownImage = citationText.match(/\[.*\]\(.*\)/);
      const encodedCitationText = isMarkdownImage ? citationText : encodeURIComponent(citationText);
      const citationId = `:cite[${encodedCitationText}]{generationId="${generationId}" start="${start}" end="${end}"}`;

      replacedText = replacedText.slice(0, citeStart) + citationId + replacedText.slice(citeEnd);
      lengthDifference += citationId.length - (citeEnd - citeStart);
    });

  if (iFrameReferences.length > 0) {
    const references = 'From: ' + formatter.format(iFrameReferences);
    replacedText = references + '\n' + replacedText;
  }

  if (notFoundReferences.length > 0 || codeBlockReferences.length > 0) {
    const allReferences = [...codeBlockReferences, ...notFoundReferences];
    const references = '\nOther references: ' + formatter.format(allReferences);
    replacedText = replacedText + '\n' + references;
  }

  return replacedText;
};

export const createStartEndKey = (start: number | string, end: number | string) =>
  `${start}-${end}`;

export function isReferenceBetweenSpecialTags(
  regExp: RegExp,
  replacedText: string,
  citeStart: number
): boolean {
  const regex = new RegExp(regExp, 'g');

  let match;
  while ((match = regex.exec(replacedText))) {
    if (match && match.index <= citeStart && citeStart <= match.index + match[0].length) {
      return true;
    }
  }

  return false;
}
