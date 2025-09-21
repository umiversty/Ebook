<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount, tick } from 'svelte';
  import type { Action } from 'svelte/action';
  import { createEpubViewAdapter, ADAPTER_MESSAGE_SOURCE } from './viewAdapter.js';
  import { interpretMenuKey } from './tocNavigation.js';
  import type {
    EpubHeading,
    EpubLandmark,
    EpubPage,
    EpubTocItem,
    EvidenceCapturePayload,
    SearchResult
  } from './types.js';

  type MessageEventData =
    | { source: string; type: 'heading'; heading: EpubHeading | null; pageId: string | null }
    | { source: string; type: 'pagechange'; pageId: string; label?: string }
    | ({ source: string; type: 'evidence' } & EvidenceCapturePayload);

  export let pages: EpubPage[] = [];
  export let toc: EpubTocItem[] = [];
  export let landmarks: EpubLandmark[] = [];
  export let initialPageId: string | undefined = undefined;

  const dispatch = createEventDispatcher<{
    pagechange: { pageId: string };
    heading: { heading: EpubHeading | null };
    evidencecapture: { payload: EvidenceCapturePayload };
  }>();

  let container: HTMLDivElement;
  let tocButtonEl: HTMLButtonElement | null = null;
  let searchInput: HTMLInputElement | null = null;
  let adapter: ReturnType<typeof createEpubViewAdapter> | null = null;
  let currentPage: EpubPage | null = null;
  let currentHeading: EpubHeading | null = null;
  let headingAnnouncement = '';
  let pageAnnouncement = '';
  let tocOpen = false;
  let searchOpen = false;
  let searchTerm = '';
  let searchResults: SearchResult[] = [];
  let menuFocusIndex = 0;
  const tocButtons: Array<HTMLButtonElement | null> = [];

  const flattenToc = (items: EpubTocItem[], acc: Array<{ item: EpubTocItem; level: number }> = [], level = 1) => {
    for (const item of items) {
      acc.push({ item, level });
      if (item.children) flattenToc(item.children, acc, level + 1);
    }
    return acc;
  };

  $: flatToc = flattenToc(toc);

  function registerMenuItem(node: HTMLButtonElement | null, index: number) {
    tocButtons[index] = node;
  }

  const menuItem: Action<HTMLButtonElement, number> = (node, index) => {
    registerMenuItem(node, index);
    return {
      update(newIndex) {
        registerMenuItem(null, index);
        registerMenuItem(node, newIndex);
      },
      destroy() {
        registerMenuItem(null, index);
      }
    };
  };

  function focusMenuIndex(index: number) {
    menuFocusIndex = index;
    const target = tocButtons[menuFocusIndex];
    if (target) target.focus();
  }

  async function toggleToc() {
    tocOpen = !tocOpen;
    if (tocOpen) {
      await tick();
      focusMenuIndex(0);
    }
  }

  function closeToc() {
    tocOpen = false;
    tocButtonEl?.focus();
  }

  function menuKeydown(event: KeyboardEvent, index: number, item: EpubTocItem) {
    if (!tocOpen) return;
    const action = interpretMenuKey(event.key, index, flatToc.length);
    switch (action.type) {
      case 'move':
        event.preventDefault();
        focusMenuIndex(action.index);
        break;
      case 'select':
        event.preventDefault();
        selectTocItem(item);
        break;
      case 'close':
        event.preventDefault();
        closeToc();
        break;
      case 'noop':
      default:
        break;
    }
  }

  function normaliseId(href: string) {
    return href.replace(/^#/, '');
  }

  function selectTocItem(item: EpubTocItem) {
    if (!adapter) return;
    const headingId = item.headingId ?? normaliseId(item.href);
    if (headingId) {
      adapter.goToHeading(headingId);
    }
    closeToc();
  }

  async function toggleSearch() {
    searchOpen = !searchOpen;
    if (searchOpen) {
      await tick();
      searchInput?.focus();
    }
  }

  function runSearch(event?: Event) {
    event?.preventDefault();
    if (!adapter) return;
    searchResults = adapter.search(searchTerm);
  }

  function activateSearchResult(result: SearchResult) {
    if (!adapter) return;
    if (result.headingId) {
      adapter.goToHeading(result.headingId);
    } else {
      adapter.goToPage(result.pageId);
    }
    searchOpen = false;
  }

  function goToOffset(direction: 'prev' | 'next') {
    if (!adapter || !currentPage) return;
    const index = pages.findIndex((page) => page.id === currentPage?.id);
    if (index < 0) return;
    if (direction === 'next' && index < pages.length - 1) {
      adapter.goToPage(pages[index + 1].id);
    }
    if (direction === 'prev' && index > 0) {
      adapter.goToPage(pages[index - 1].id);
    }
  }

  function handleMessage(event: MessageEvent<MessageEventData>) {
    const data = event.data;
    if (!data || typeof data !== 'object') return;
    if (data.source !== ADAPTER_MESSAGE_SOURCE) return;
    if (data.type === 'heading') {
      headingAnnouncement = data.heading?.text ?? '';
      currentHeading = data.heading ?? null;
      dispatch('heading', { heading: currentHeading });
    }
    if (data.type === 'pagechange') {
      pageAnnouncement = data.label ? `Page ${data.label}` : `Page ${data.pageId}`;
      dispatch('pagechange', { pageId: data.pageId });
    }
    if (data.type === 'evidence') {
      const { pageId, text, start, end } = data;
      dispatch('evidencecapture', { payload: { pageId, text, start, end } });
    }
  }

  onMount(() => {
    if (!container) return;
    adapter = createEpubViewAdapter({
      container,
      pages,
      toc,
      landmarks,
      initialPageId
    });
    const unsubPage = adapter.currentPage.subscribe((page: EpubPage | null) => {
      currentPage = page;
    });
    const unsubHeading = adapter.currentHeading.subscribe((heading: EpubHeading | null) => {
      currentHeading = heading;
      headingAnnouncement = heading?.text ?? '';
    });
    adapter.mount();
    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
      unsubPage();
      unsubHeading();
    };
  });

  onDestroy(() => {
    adapter?.destroy();
  });
</script>

<svelte:window on:message={handleMessage} />

<div class="epub-reader">
  <div class="controls" aria-label="Reader controls">
    <button
      class="control"
      bind:this={tocButtonEl}
      type="button"
      aria-haspopup="true"
      aria-expanded={tocOpen}
      on:click={toggleToc}
    >
      Table of contents
    </button>
    <button class="control" type="button" on:click={toggleSearch} aria-expanded={searchOpen} aria-controls="epub-search">
      Search book
    </button>
    <div class="spacer" aria-hidden="true"></div>
    <button class="control" type="button" on:click={() => goToOffset('prev')} disabled={!currentPage || pages[0]?.id === currentPage?.id}>
      Previous section
    </button>
    <button class="control" type="button" on:click={() => goToOffset('next')} disabled={!currentPage || pages[pages.length - 1]?.id === currentPage?.id}>
      Next section
    </button>
  </div>

  {#if tocOpen}
    <nav class="toc" aria-label="EPUB table of contents">
      <ul role="menu" aria-label="Chapter list">
        {#each flatToc as entry, index}
          <li role="none" class={`toc-item level-${entry.level}`}>
            <button
              use:menuItem={index}
              type="button"
              role="menuitem"
              tabindex={tocOpen && index === menuFocusIndex ? 0 : -1}
              on:click={() => selectTocItem(entry.item)}
              on:keydown={(event) => menuKeydown(event, index, entry.item)}
            >
              {entry.item.title}
            </button>
          </li>
        {/each}
      </ul>
    </nav>
  {/if}

  {#if searchOpen}
    <form id="epub-search" class="search" role="search" aria-label="Search EPUB" on:submit={runSearch}>
      <label>
        <span class="sr-only">Search term</span>
        <input
          bind:this={searchInput}
          type="search"
          placeholder="Search in book"
          aria-label="Search in book"
          bind:value={searchTerm}
        />
      </label>
      <button class="control" type="submit">Search</button>
    </form>
    {#if searchResults.length > 0}
      <ul class="search-results" role="list">
        {#each searchResults as result, index}
          <li>
            <button type="button" on:click={() => activateSearchResult(result)}>
              <span class="muted">Result {index + 1}:</span> {result.snippet}
            </button>
          </li>
        {/each}
      </ul>
    {:else if searchTerm.trim().length > 0}
      <p role="note">No results for “{searchTerm}”.</p>
    {/if}
  {/if}

  <div class="status-bar">
    <div role="status" aria-live="polite" aria-atomic="true" aria-label="Current heading announcement">
      {headingAnnouncement}
    </div>
    <div class="muted" aria-live="polite" aria-atomic="true">{pageAnnouncement}</div>
  </div>

  <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
  <div
    class="viewer"
    bind:this={container}
    tabindex="0"
    role="document"
    aria-label="EPUB reading surface"
    aria-describedby="landmark-list"
  >
    {#if currentPage}
      <article class="page" aria-roledescription="EPUB page" data-page={currentPage.label}>
        {@html currentPage.html}
      </article>
    {:else}
      <p>No EPUB content available.</p>
    {/if}
  </div>

  <dl id="landmark-list" class="landmarks">
    {#each landmarks as landmark}
      <div>
        <dt class="muted">{landmark.title}</dt>
        <dd>{landmark.href}</dd>
      </div>
    {/each}
  </dl>
</div>

<style>
  .epub-reader {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .control {
    background: #7c9cff;
    color: #0b1020;
    border: none;
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
  }

  .control:focus {
    outline: none;
  }

  .control:focus-visible {
    box-shadow: 0 0 0 4px rgba(195, 212, 255, 0.85);
  }

  .control[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spacer {
    flex: 1;
  }

  .toc {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 12px;
    max-height: 240px;
    overflow: auto;
  }

  .toc-item button {
    width: 100%;
    text-align: left;
    padding: 6px;
    background: transparent;
    color: inherit;
    border: 1px solid transparent;
    border-radius: 6px;
  }

  .toc-item button:focus {
    outline: none;
  }

  .toc-item button:focus-visible {
    border-color: rgba(124, 156, 255, 0.75);
    background: rgba(124, 156, 255, 0.2);
    box-shadow: 0 0 0 4px rgba(124, 156, 255, 0.55);
  }

  .toc-item.level-2 { padding-left: 16px; }
  .toc-item.level-3 { padding-left: 32px; }

  .search {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .search input {
    padding: 8px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.2);
    color: inherit;
  }

  .search-results {
    display: grid;
    gap: 8px;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .search-results button {
    width: 100%;
    text-align: left;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: rgba(255, 255, 255, 0.05);
    color: inherit;
  }

  .search-results button:focus {
    outline: none;
  }

  .search-results button:focus-visible {
    border-color: rgba(124, 156, 255, 0.75);
    background: rgba(124, 156, 255, 0.2);
    box-shadow: 0 0 0 4px rgba(124, 156, 255, 0.55);
  }

  .status-bar {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .viewer {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 16px;
    min-height: 320px;
    line-height: 1.8;
    outline: none;
  }

  .viewer:focus-visible {
    box-shadow: 0 0 0 3px rgba(124, 156, 255, 0.6);
  }

  .landmarks {
    display: grid;
    gap: 4px;
    margin: 0;
  }

  .muted {
    color: #9aa3b2;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }
</style>
