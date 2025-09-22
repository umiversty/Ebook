import type { EpubHeading } from '../epub/types.js';
import type { PdfOutlineItem } from '../pdf/types.js';

export type ReadingLocationSource = 'epub' | 'pdf';

export interface ReadingLocation {
  source: ReadingLocationSource;
  pageId: string;
  pageLabel?: string;
  depth?: number;
}

export interface TextSpan {
  start: number;
  end: number;
}

export interface ReadingSection {
  id: string;
  title: string;
  location: ReadingLocation;
  textSpan: TextSpan | null;
}

export type ReadingSectionInit = {
  id: string;
  title: string;
  location: ReadingLocation;
  textSpan?: TextSpan | null;
};

export function createReadingSection(init: ReadingSectionInit): ReadingSection {
  return {
    id: init.id,
    title: init.title,
    location: init.location,
    textSpan: init.textSpan ?? null
  };
}

export function createSectionFromEpubHeading(args: {
  heading: EpubHeading;
  pageId: string;
  pageLabel?: string;
}): ReadingSection {
  const { heading, pageId, pageLabel } = args;
  return createReadingSection({
    id: heading.id,
    title: heading.text,
    location: {
      source: 'epub',
      pageId,
      pageLabel,
      depth: heading.level
    }
  });
}

export function createSectionFromPdfOutline(args: {
  item: PdfOutlineItem;
  pageLabel?: string;
}): ReadingSection {
  const { item, pageLabel } = args;
  return createReadingSection({
    id: item.id,
    title: item.title,
    location: {
      source: 'pdf',
      pageId: String(item.pageNumber),
      pageLabel,
      depth: item.depth
    },
    textSpan: item.textSpan ?? null
  });
}
