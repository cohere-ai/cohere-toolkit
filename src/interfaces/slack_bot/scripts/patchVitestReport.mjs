// The ArtiomTr/jest-coverage-report-action GitHub action requires that Vitest's JSON coverage report
// is structured like Jest's, where the `coverageMap` value is the data from Vitest's `coverage-final.json`.
// This script patches the report to match the expected structure.
// See https://github.com/ArtiomTr/jest-coverage-report-action/issues/244#issuecomment-1260555231
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const testReportFilename = path.join(__dirname, '..', 'coverage', 'report.json');
const coverageReportFilename = path.join(__dirname, '..', 'coverage', 'coverage-final.json');

const testReport = JSON.parse(await fs.readFile(testReportFilename, 'utf8'));
const coverageReport = JSON.parse(await fs.readFile(coverageReportFilename, 'utf8'));

testReport.coverageMap = coverageReport;

await fs.writeFile(testReportFilename, JSON.stringify(testReport));
console.log('Coverage report appended to ' + testReportFilename);
