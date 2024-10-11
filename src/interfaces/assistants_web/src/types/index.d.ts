type Nullable<T> = T | null;

declare module 'js-resume-parser' {
  export function getDataFromPDF(file: File): Promise<{ text: string }>;
  export function getDataFromDocx(file: File): Promise<{ text: string }>;
}
