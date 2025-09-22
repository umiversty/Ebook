import { get, writable, type Readable } from 'svelte/store';
import type {
  EpubHeading,
  EpubLandmark,
  EpubPage,
  EpubTocItem,
  EvidenceCapturePayload,
  SearchResult
} from './types.js';
import { createSectionFromEpubHeading, type ReadingSection } from '../reader/readingSection.js';

export const ADAPTER_MESSAGE_SOURCE = 'epub-adapter';

export interface AdapterConfig {
  container: HTMLElement;
  pages: EpubPage[];
  toc: EpubTocItem[];
  landmarks: EpubLandmark[];
  initialPageId?: string;
  onPageChange?: (pageId: string) => void;
  onHeadingChange?: (section: ReadingSection | null) => void;
  onEvidenceCapture?: (payload: EvidenceCapturePayload) => void;
}

export interface EpubViewAdapter {
  currentPage: Readable<EpubPage | null>;
  currentHeading: Readable<ReadingSection | null>;
  mount(): void;
  destroy(): void;
  goToPage(pageId: string): void;
  goToHeading(headingId: string): void;
  search(term: string): SearchResult[];
  getPageList(): EpubPage[];
  getLandmarks(): EpubLandmark[];
}

function emitMessage(type: string, payload: Record<string, unknown>) {
  window.postMessage({ source: ADAPTER_MESSAGE_SOURCE, type, ...payload }, '*');
}

function normalise(str: string): string {
  return str.replace(/\s+/g, ' ').trim();
}

function stripHtml(html: string): string {
  return normalise(html.replace(/<[^>]+>/g, ' '));
}

export function createEpubViewAdapter(config: AdapterConfig): EpubViewAdapter {
  const { container, pages, initialPageId, onPageChange, onHeadingChange, onEvidenceCapture } = config;
  const currentPage = writable<EpubPage | null>(null);
  const currentHeading = writable<ReadingSection | null>(null);

  let mounted = false;

  const pageIndex = new Map<string, EpubPage>();
  for (const page of pages) {
    pageIndex.set(page.id, page);
  }

  function toReadingSection(heading: EpubHeading | null, pageId: string | null): ReadingSection | null {
    if (!heading) return null;
    const safePageId = pageId ?? heading.id;
    const page = pageIndex.get(safePageId);
    return createSectionFromEpubHeading({
      heading,
      pageId: safePageId,
      pageLabel: page?.label
    });
  }

  function setHeading(heading: EpubHeading | null, pageId: string | null) {
    const section = heading ? toReadingSection(heading, pageId) : null;
    currentHeading.set(section);
    onHeadingChange?.(section);
    emitMessage('heading', { heading: section, pageId });
  }

  function setPage(page: EpubPage | null) {
    currentPage.set(page);
    if (page) {
      container.dataset.pageId = page.id;
      onPageChange?.(page.id);
      emitMessage('pagechange', { pageId: page.id, label: page.label });
      const defaultHeading = page.headings[0] ?? null;
      setHeading(defaultHeading, page.id);
    } else {
      delete container.dataset.pageId;
      setHeading(null, null);
    }
  }

  function goToPage(pageId: string) {
    const next = pageIndex.get(pageId);
    if (!next) return;
    setPage(next);
  }

  function goToHeading(headingId: string) {
    for (const page of pages) {
      const heading = page.headings.find((h: EpubHeading) => h.id === headingId);
      if (heading) {
        setPage(page);
        setHeading(heading, page.id);
        return;
      }
    }
  }

  function search(term: string): SearchResult[] {
    const query = normalise(term).toLowerCase();
    if (!query) return [];
    const results: SearchResult[] = [];
    for (const page of pages) {
      const text = stripHtml(page.html);
      const idx = text.toLowerCase().indexOf(query);
      if (idx >= 0) {
        const start = Math.max(0, idx - 40);
        const end = Math.min(text.length, idx + query.length + 40);
        const snippet = `${idx > 0 ? '…' : ''}${text.slice(start, end)}${end < text.length ? '…' : ''}`;
        const heading = page.headings.find((h: EpubHeading) => h.level <= 2) ?? page.headings[0];
        results.push({ pageId: page.id, headingId: heading?.id, snippet });
      }
    }
    return results;
  }

  function getPageList(): EpubPage[] {
    return [...pages];
  }

  function getLandmarks() {
    return [...config.landmarks];
  }

  function handleSelection() {
    const selection = window.getSelection?.();
    if (!selection || selection.rangeCount === 0) return;
    const range = selection.getRangeAt(0);
    if (!container.contains(range.commonAncestorContainer)) return;
    const text = selection.toString();
    if (!text || normalise(text).length < 3) return;

    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
    let acc = 0;
    let startGlobal = -1;
    let endGlobal = -1;
    while (walker.nextNode()) {
      const node = walker.currentNode as Text;
      if (node === range.startContainer) startGlobal = acc + range.startOffset;
      if (node === range.endContainer) {
        endGlobal = acc + range.endOffset;
        break;
      }
      acc += node.nodeValue?.length ?? 0;
    }

    const page = get(currentPage);
    if (page && startGlobal >= 0 && endGlobal > startGlobal) {
      const payload: EvidenceCapturePayload = {
        text,
        start: startGlobal,
        end: endGlobal,
        pageId: page.id
      };
      onEvidenceCapture?.(payload);
      emitMessage('evidence', { ...payload });
    }
    selection.removeAllRanges();
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (!mounted) return;
    if (event.key === 'PageDown' || (event.key === 'ArrowRight' && event.altKey)) {
      event.preventDefault();
      const page = get(currentPage);
      if (!page) return;
      const index = pages.findIndex((p) => p.id === page.id);
      if (index >= 0 && index < pages.length - 1) {
        goToPage(pages[index + 1].id);
      }
    }
    if (event.key === 'PageUp' || (event.key === 'ArrowLeft' && event.altKey)) {
      event.preventDefault();
      const page = get(currentPage);
      if (!page) return;
      const index = pages.findIndex((p) => p.id === page.id);
      if (index > 0) {
        goToPage(pages[index - 1].id);
      }
    }
  }

  function mount() {
    if (mounted) return;
    mounted = true;
    container.addEventListener('mouseup', handleSelection);
    container.addEventListener('keydown', handleKeyDown);

    const initial = initialPageId ? pageIndex.get(initialPageId) : pages[0];
    if (initial) {
      setPage(initial);
    } else {
      setPage(null);
    }
  }

  function destroy() {
    if (!mounted) return;
    mounted = false;
    container.removeEventListener('mouseup', handleSelection);
    container.removeEventListener('keydown', handleKeyDown);
  }

  return {
    currentPage,
    currentHeading,
    mount,
    destroy,
    goToPage,
    goToHeading,
    search,
    getPageList,
    getLandmarks
  };
}
