import { Citation } from '@/cohere-client';

/**
 * @description Helper function to temporarily ensure markdown image syntax provided by the model is correct.
 * This is a temporary fix as the current model is consistently returning incorrect markdown image syntax.
 * @param text - message text or citation text
 */
export const fixMarkdownImagesInText = (text: string) => {
  return text.replace('! [', '![');
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
  let replacedText = text;

  let lengthDifference = 0; // Track the cumulative length difference
  citations.forEach(({ start = 0, end = 0, text: citationText }) => {
    const citeStart = start + lengthDifference;
    const citeEnd = end + lengthDifference;

    const fixedText = fixMarkdownImagesInText(citationText);

    // Encode the citationText in case there are any weird characters or unclosed brackets that will
    // interfere with parsing the markdown. However, let markdown images through so they may be properly
    // rendered.
    const isMarkdownImage = fixedText.match(/!\[.*\]\(.*\)/);
    const encodedCitationText = isMarkdownImage ? fixedText : encodeURIComponent(fixedText);
    const citationId = `:cite[${encodedCitationText}]{generationId="${generationId}" start="${start}" end="${end}"}`;

    replacedText = replacedText.slice(0, citeStart) + citationId + replacedText.slice(citeEnd);
    lengthDifference += citationId.length - (citeEnd - citeStart);
  });
  return replacedText;
};

export const createStartEndKey = (start: number | string, end: number | string) =>
  `${start}-${end}`;
