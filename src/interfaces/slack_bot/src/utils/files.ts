import { FileShareMessageEvent } from '@slack/bolt';
import { FileElement } from '@slack/web-api/dist/response/ConversationsRepliesResponse';
import * as pdfjs from 'pdfjs-dist';
import { TextItem } from 'pdfjs-dist/types/src/display/api';
import WORDEXTRACTOR from 'word-extractor';

export type SlackFile = Exclude<FileShareMessageEvent['files'], undefined>[number] | FileElement;

export type PageText = {
  text: string;
  pageNumber: number;
};

const getPDFText = async (fileData: ArrayBuffer): Promise<string> => {
  const pageTexts = await getPdfPageTexts(fileData);

  return pageTexts.map((p) => p.text).join(' ');
};

const getPdfPageTexts = async (fileData: ArrayBuffer): Promise<PageText[]> => {
  const pdfDocument = await pdfjs.getDocument({ data: fileData, useSystemFonts: true }).promise;
  const pageNumbers = [...Array(pdfDocument.numPages + 1).keys()].splice(1);

  const pageTexts = await Promise.all(
    pageNumbers.map(async (pageNumber) => {
      const page = await pdfDocument.getPage(pageNumber);
      const tokenizedText = await page.getTextContent();
      const text = tokenizedText.items.map((token) => (token as TextItem).str).join(' ');
      return {
        text,
        pageNumber,
      };
    }),
  );

  return pageTexts;
};

const getDocText = async (fileData: Buffer): Promise<string> => {
  const extractor = new WORDEXTRACTOR();
  const extracted = await extractor.extract(fileData);
  return extracted.getBody();
};

const getSafeFileBuffer = (data: ArrayBuffer): Buffer => {
  // Anti-corruption layer
  const temp = Buffer.alloc(data.byteLength);
  const view = Buffer.from(data);
  view.copy(temp);

  return view;
};

/**
 * Given an input file buffer return the entire content of the file as a string
 */
export const getFileRawText = async (file: SlackFile, buffer: ArrayBuffer): Promise<string> => {
  switch (file.filetype) {
    case 'pdf':
      return getPDFText(buffer);
    case 'doc':
    case 'docx':
      return getDocText(getSafeFileBuffer(buffer));
    case 'text':
      return getSafeFileBuffer(buffer).toString('utf8');
    default:
      throw new Error('Unsupported file type');
  }
};

/**
 * Given an input file buffer return the content of the file as chunks broken down by page
 */
export const getFileChunks = async (file: SlackFile, buffer: ArrayBuffer): Promise<PageText[]> => {
  switch (file.filetype) {
    case 'pdf':
      return await getPdfPageTexts(buffer);
    default:
      throw new Error('Unsupported file type');
  }
};
