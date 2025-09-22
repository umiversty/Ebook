import { cleanup, render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import ProofofReading from '../../../../ProofofReading.svelte';
import { ADAPTER_MESSAGE_SOURCE } from '../viewAdapter.js';
import type { ReadingSection } from '../../reader/readingSection.js';
import { setViewportWidth as setViewportWidthStore } from '../../reader/viewportStore.js';

const DEFAULT_VIEWPORT = 1024;
const setViewportWidth = (width: number) => {
  Object.defineProperty(window, 'innerWidth', { configurable: true, writable: true, value: width });
  setViewportWidthStore(width);
};
const originalMatchMedia = window.matchMedia;

describe('Proof-of-Reading header integrations', () => {
  beforeEach(() => {
    setViewportWidth(DEFAULT_VIEWPORT);
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      writable: true,
      value: vi.fn().mockImplementation((query: string) => {
        const match = /max-width:\s*(\d+)px/.exec(query);
        const limit = match ? Number(match[1]) : Number.NaN;
        const matches = Number.isFinite(limit) ? window.innerWidth <= limit : false;
        return {
          matches,
          media: query,
          onchange: null,
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          addListener: vi.fn(),
          removeListener: vi.fn(),
          dispatchEvent: vi.fn()
        };
      })
    });
  });

  afterEach(() => {
    cleanup();
    setViewportWidth(DEFAULT_VIEWPORT);
    if (originalMatchMedia) {
      Object.defineProperty(window, 'matchMedia', {
        configurable: true,
        writable: true,
        value: originalMatchMedia
      });
    } else {
      // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
      delete (window as { matchMedia?: unknown }).matchMedia;
    }
  });

  test('renders breadcrumb trail with accessible current section', () => {
    render(ProofofReading);
    const nav = screen.getByRole('navigation', { name: /course navigation/i });
    const links = nav.querySelectorAll('a.breadcrumb__link');
    expect(links.length).toBe(4);

    const currentLink = Array.from(links).find((link) => link.getAttribute('aria-current') === 'page');
    expect(currentLink?.textContent?.trim()).toBe('Overview');
  });

  test('exposes progress ring status text for assistive tech', () => {
    render(ProofofReading);
    const progressRing = screen.getByRole('img', { name: /session progress: 0% complete/i });
    expect(progressRing).toBeInstanceOf(HTMLElement);
    expect(progressRing.getAttribute('aria-label')).to.contain('0% complete');
  });

  test('collapses breadcrumb trail when the viewport is narrow', async () => {
    render(ProofofReading);
    let nav = screen.getByRole('navigation', { name: /course navigation/i });
    expect(nav.querySelectorAll('a.breadcrumb__link').length).toBe(4);

    setViewportWidth(600);
    window.dispatchEvent(new Event('resize'));
    await tick();
    await tick();

    nav = screen.getByRole('navigation', { name: /course navigation/i });
    const visibleLinks = nav.querySelectorAll('a.breadcrumb__link');
    expect(visibleLinks.length).toBe(2);
    expect(Array.from(visibleLinks).map((node) => node.textContent?.trim())).toEqual([
      'Colonial Rationing Case Study',
      'Overview'
    ]);

    const overflowButton = screen.getByRole('button', { name: /previous levels/i });
    expect(overflowButton).toBeInstanceOf(HTMLButtonElement);
  });

  test('updates breadcrumb when the reader emits a new section', async () => {
    render(ProofofReading);
    const nextSection: ReadingSection = {
      id: 'chapter-implementation-audits',
      title: 'Audits and Oversight',
      location: { source: 'epub', pageId: 'page-2', pageLabel: '2', depth: 2 },
      textSpan: null
    };

    window.dispatchEvent(
      new MessageEvent('message', {
        data: { source: ADAPTER_MESSAGE_SOURCE, type: 'heading', heading: nextSection, pageId: 'page-2' }
      })
    );
    await tick();

    const nav = screen.getByRole('navigation', { name: /course navigation/i });
    expect(nav.textContent).toContain('Audits and Oversight');

    const status = screen.getByText(/Current section:/i);
    expect(status.textContent).toContain('Audits and Oversight');
  });
});
