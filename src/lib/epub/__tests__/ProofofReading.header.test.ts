<<<<<<< HEAD
// src/lib/epub/__tests__/ProofofReading.header.test.ts
import { render, screen } from '@testing-library/svelte';
import { vi } from 'vitest';
import ProofofReading from '../../../ProofofReading.svelte';

// Mock window.innerWidth so responsive breadcrumb works
function setViewport(width: number) {
  vi.stubGlobal('window', {
    innerWidth: width,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    matchMedia: () => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn()
    })
  });
}

describe('Proof-of-Reading header integrations', () => {
  it('renders breadcrumb trail with accessible current section', async () => {
    setViewport(1200);
    render(ProofofReading);

    const nav = await screen.findByRole('navigation', {
      name: /course navigation/i
=======
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
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
    });
    expect(nav).toBeInTheDocument();

    // Current page breadcrumb should have aria-current="page"
    expect(nav.querySelector('[aria-current="page"]')).toBeTruthy();
  });

  it('exposes progress ring status text for assistive tech', async () => {
    setViewport(1200);
    render(ProofofReading);

    const ring = await screen.findByRole('img', {
      name: /session progress: \d+% complete/i
    });
    expect(ring).toBeInTheDocument();
  });

  it('collapses breadcrumb trail when the viewport is narrow', async () => {
    setViewport(500);
    render(ProofofReading);

<<<<<<< HEAD
    // Expect the overflow "…" button to appear for hidden breadcrumbs
    const overflowBtn = await screen.findByRole('button', {
      name: /previous levels:/i
    });
    expect(overflowBtn).toBeInTheDocument();
=======
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
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
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
