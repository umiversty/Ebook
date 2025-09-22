import { describe, expect, test } from 'vitest';
import { mapPdfOutlineToSections } from '../outlineAdapter.js';
import type { PdfOutlineItem } from '../types.js';

describe('PDF outline adapter', () => {
  test('maps outline items to reading sections with location metadata', () => {
    const outline: PdfOutlineItem[] = [
      { id: 'outline-1', title: 'Preface', pageNumber: 1, depth: 1 },
      {
        id: 'outline-1-1',
        title: 'Mission Statement',
        pageNumber: 2,
        depth: 2,
        textSpan: { start: 120, end: 220 }
      }
    ];

    const result = mapPdfOutlineToSections({
      outline,
      getPageLabel: (pageNumber) => `Page ${pageNumber}`
    });

    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      id: 'outline-1',
      title: 'Preface',
      location: { source: 'pdf', pageId: '1', depth: 1, pageLabel: 'Page 1' },
      textSpan: null
    });
    expect(result[1]).toMatchObject({
      id: 'outline-1-1',
      title: 'Mission Statement',
      location: { source: 'pdf', pageId: '2', depth: 2, pageLabel: 'Page 2' },
      textSpan: { start: 120, end: 220 }
    });
  });
});
