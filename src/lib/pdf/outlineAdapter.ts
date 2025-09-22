import type { PdfOutlineItem } from './types.js';
import type { ReadingSection } from '../reader/readingSection.js';
import { createSectionFromPdfOutline } from '../reader/readingSection.js';

export interface PdfOutlineAdapterConfig {
  outline: PdfOutlineItem[];
  getPageLabel?: (pageNumber: number) => string | undefined;
}

export function mapPdfOutlineToSections(config: PdfOutlineAdapterConfig): ReadingSection[] {
  const { outline, getPageLabel } = config;
  return outline.map((item) =>
    createSectionFromPdfOutline({
      item,
      pageLabel: getPageLabel?.(item.pageNumber)
    })
  );
}
