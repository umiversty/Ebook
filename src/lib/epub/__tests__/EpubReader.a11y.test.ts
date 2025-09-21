import { beforeEach, afterEach, describe, expect, test, vi } from 'vitest';
import { createEpubViewAdapter } from '../viewAdapter.js';
import { interpretMenuKey } from '../tocNavigation.js';
import { sampleLandmarks, samplePages, sampleToc } from '../sampleData.js';

const originalPostMessage = window.postMessage;

describe('EPUB accessibility integrations', () => {
  const messages: Array<Record<string, unknown>> = [];

  beforeEach(() => {
    vi.spyOn(window, 'postMessage').mockImplementation((message: any) => {
      if (typeof message === 'object') {
        messages.push(message as Record<string, unknown>);
      }
    });
  });

  afterEach(() => {
    messages.length = 0;
    vi.restoreAllMocks();
    window.postMessage = originalPostMessage;
  });

  test('view adapter emits heading announcements when navigating', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const adapter = createEpubViewAdapter({
      container,
      pages: samplePages,
      toc: sampleToc,
      landmarks: sampleLandmarks
    });

    adapter.mount();

    let headingMessage = messages.find((msg) => msg.type === 'heading');
    expect(headingMessage && (headingMessage.heading as any)?.text).toContain('Colonial Rationing');

    messages.length = 0;
    adapter.goToPage('page-2');
    headingMessage = messages.find((msg) => msg.type === 'heading');
    expect(headingMessage && (headingMessage.heading as any)?.text).toContain('Implementation');

    adapter.destroy();
    container.remove();
  });

  test('table of contents keyboard interactions are interpreted correctly', () => {
    expect(interpretMenuKey('ArrowDown', 0, 3)).toEqual({ type: 'move', index: 1 });
    expect(interpretMenuKey('ArrowUp', 0, 3)).toEqual({ type: 'move', index: 2 });
    expect(interpretMenuKey('Home', 2, 3)).toEqual({ type: 'move', index: 0 });
    expect(interpretMenuKey('End', 1, 4)).toEqual({ type: 'move', index: 3 });
    expect(interpretMenuKey('Enter', 2, 4)).toEqual({ type: 'select' });
    expect(interpretMenuKey('Escape', 2, 4)).toEqual({ type: 'close' });
    expect(interpretMenuKey('KeyZ', 0, 4)).toEqual({ type: 'noop' });
  });
});
