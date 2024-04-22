import { Citation } from '@/cohere-client';

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
  let replacedText = text;

  let lengthDifference = 0; // Track the cumulative length difference
  citations.forEach(({ start = 0, end = 0, text: citationText }) => {
    const citeStart = start + lengthDifference;
    const citeEnd = end + lengthDifference;
    // Encode the citationText in case there are any weird characters or unclosed brackets that will
    // interfere with parsing the markdown.
    const citationId = `:cite[${encodeURIComponent(
      citationText ?? ''
    )}]{generationId="${generationId}" start="${start}" end="${end}"}`;
    replacedText = replacedText.slice(0, citeStart) + citationId + replacedText.slice(citeEnd);
    lengthDifference += citationId.length - (citeEnd - citeStart);
  });
  return replacedText;
};

export const createStartEndKey = (start: number | string, end: number | string) =>
  `${start}-${end}`;
