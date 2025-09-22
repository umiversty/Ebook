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

    // Expect the overflow "…" button to appear for hidden breadcrumbs
    const overflowBtn = await screen.findByRole('button', {
      name: /previous levels:/i
    });
    expect(overflowBtn).toBeInTheDocument();
  });
});
