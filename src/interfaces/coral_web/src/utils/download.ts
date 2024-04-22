export type StructuredTable = {
  header: string[];
  rows: string[][];
};

/**
 * A client-side function that triggers a file download in the user's browser.
 * Note: This creates a temporary <a /> tag in the document body and simulates a click on it which may not always work
 * https://stackoverflow.com/questions/50694881/how-to-download-file-in-react-js/50695407#50695407
 *
 * @param fileName The name of the file
 * @param parts Data that will comprise the file
 * @param type MIME-type of the data
 *
 * @returns True If the download was successful, else False
 */
export function downloadFile(
  fileName: string,
  parts: BlobPart[],
  type: string = 'text/plain'
): boolean {
  if (window === null || window === undefined || document === null || document === undefined) {
    return false;
  }

  const file = new File(parts, fileName, { type: type });
  const link = document.createElement('a');
  const url = URL.createObjectURL(file);

  try {
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    // schedule a removal in the next event loop
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 0);
  } catch (e) {
    return false;
  }

  return true;
}

/**
 * Converts an object of type StructuredTable into a string representation of an XSV
 *
 * Ex 1: Using the delimiter ',' will result in a CSV file (comma seperated)
 * Ex 2: Using the delimiter '\t' will result in a TSV file (tab seperated)
 * @param table An object of type StructuredTable
 * @param delimiter A delimiter for the XSV (ex: ',' or '\t')
 */
export function structuredTableToXSV(
  table: StructuredTable | null,
  delimiter: string = ','
): string | null {
  if (!table || table.header.length === 0 || table.rows.length === 0) return null;

  let xsv = '';
  table.header.forEach(
    (txt, i) => (xsv += `"${txt}"${i < table.header.length - 1 ? delimiter : ''}`)
  );
  xsv += '\n';
  table.rows.forEach((row) => {
    row.forEach((txt, i) => (xsv += `"${txt}"${i < row.length - 1 ? delimiter : ''}`));
    xsv += '\n';
  });

  return xsv;
}
