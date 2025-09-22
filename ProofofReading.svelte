<script lang="ts">
  import EpubReader from './src/lib/epub/EpubReader.svelte';
  import { sampleLandmarks, samplePages, sampleToc } from './src/lib/epub/sampleData.js';
  import type { EvidenceCapturePayload } from './src/lib/epub/types.js';
  import { applyKeyboardResize, clampColumnPx, fractionToPx, MIN_COLUMN_PX, pxToFraction } from './splitLayout';

  import QuestionPanel from './src/lib/teacher/QuestionPanel.svelte';
  import { createSectionFromEpubHeading, type ReadingSection } from './src/lib/reader/readingSection.js';
  import { setViewportWidth as updateViewportStore, viewportWidthStore } from './src/lib/reader/viewportStore.js';


  // ---------------- Types ----------------
  type Task = { id: string; type: 'highlight' | 'short' | 'vocab'; prompt: string; done?: boolean; answer?: string };
  type Evidence = { id: string; text: string; start: number; end: number; pageId: string };
  type StudentRow = { name: string; time: string; tasks: string; quality: 'Strong' | 'Medium' | 'Weak'; flags?: string; flagsDemo?: boolean };

  // --------------- State -----------------
  let screen: 'student' | 'teacher' = 'student';
  const MIN_PX = MIN_COLUMN_PX;
  const BREAKPOINT = 720;
  const KEYBOARD_STEP = 32;
  const PREFERS_REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)';

  let leftWidth = 0.62;
  let rightWidth = 0.38;
  let containerWidth = 0;
  let isSingleColumn = false;
  let prefersReducedMotion = false;
  let studentGridEl: HTMLDivElement | null = null;
  let separatorEl: HTMLDivElement | null = null;
  let activePointerId: number | null = null;
  let isDragging = false;
  let dragFrame: number | null = null;
  let title = 'Colonial Rationing Case Study';

  let tasks: Task[] = [
    { id: 't1', type: 'highlight', prompt: 'Highlight the sentence where the author explains why rationing was necessary.' },
    { id: 't2', type: 'short', prompt: 'Summarize paragraph 2 in your own words (1–2 sentences).' },
    { id: 't3', type: 'vocab', prompt: 'Define the term “ration”.' }
  ];

  let evidence: Evidence[] = [];
  const initialSection = samplePages[0]?.headings[0]
    ? createSectionFromEpubHeading({
        heading: samplePages[0].headings[0],
        pageId: samplePages[0].id,
        pageLabel: samplePages[0].label
      })
    : null;
  let currentSection: ReadingSection | null = initialSection;
  let currentPageId: string | null = samplePages[0]?.id ?? null;
  let dwellMs = 0;
  let viewportWidth = BREAKPOINT;
  const unsubscribeViewport = viewportWidthStore.subscribe((value) => {
    viewportWidth = value;
  });

  type BreadcrumbNode = { id: string; label: string; href: string; isCurrent?: boolean };
  const COURSE_BREADCRUMB: BreadcrumbNode = {
    id: 'course',
    label: 'AP U.S. History',
    href: '#course'
  };
  const UNIT_BREADCRUMB: BreadcrumbNode = {
    id: 'unit',
    label: 'Unit 7 · Domestic Impacts',
    href: '#unit'
  };
  const PROGRESS_RING_RADIUS = 20;
  const PROGRESS_RING_STROKE = 4;
  const PROGRESS_RING_DIAMETER = PROGRESS_RING_RADIUS * 2 + PROGRESS_RING_STROKE * 2;
  const PROGRESS_RING_CIRCUMFERENCE = 2 * Math.PI * PROGRESS_RING_RADIUS;
  const BREADCRUMB_SEPARATOR = ' › ';

  function syncViewportWidth() {
    if (typeof window === 'undefined') return;
    const width = window.innerWidth;
    if (width !== viewportWidth) {
      updateViewportStore(width);
    }
  }

  function isMobileWidth(width: number): boolean {
    if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
      try {
        const query = window.matchMedia(`(max-width: ${BREAKPOINT - 1}px)`);
        if (typeof query.matches === 'boolean') {
          return query.matches;
        }
      } catch {
        // ignore matchMedia errors in non-browser environments
      }
    }
    return width < BREAKPOINT;
  }

  function resolveSectionLabel(section: ReadingSection | null, chapterTitle: string): string {
    if (!section) return 'Section overview';
    if (section.title.trim() === chapterTitle.trim()) {
      return 'Overview';
    }
    return section.title;
  }
  let chapterBreadcrumb: BreadcrumbNode = { id: 'chapter', label: title, href: '#chapter' };
  let sectionBreadcrumb: BreadcrumbNode = {
    id: 'section',
    label: resolveSectionLabel(currentSection, title),
    href: '#section',
    isCurrent: true
  };
  let breadcrumbTrail: BreadcrumbNode[] = [COURSE_BREADCRUMB, UNIT_BREADCRUMB, chapterBreadcrumb, sectionBreadcrumb];
  let isMobileBreadcrumb = isMobileWidth(viewportWidth);
  let visibleBreadcrumbTrail: BreadcrumbNode[] = breadcrumbTrail;
  let hiddenBreadcrumbTrail: BreadcrumbNode[] = [];
  let breadcrumbAriaLabel = `Course navigation: ${breadcrumbTrail.map((crumb) => crumb.label).join(BREADCRUMB_SEPARATOR)}`;
  let hiddenBreadcrumbLabel = '';
  onMount(() => {
    const interval = setInterval(() => {
      dwellMs += 1000;
    }, 1000);

    syncViewportWidth();

    const gridEl = studentGridEl;
    if (gridEl) {
      const initialWidth = gridEl.getBoundingClientRect().width;
      if (initialWidth) applyContainerMetrics(initialWidth);
    }

    let resizeObserver: ResizeObserver | null = null;
    let viewportResizeCleanup: (() => void) | null = null;
    if (gridEl && typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver((entries) => {
        const entry = entries[0];
        if (!entry) return;
        applyContainerMetrics(entry.contentRect.width);
      });
      resizeObserver.observe(gridEl);
    }

    if (typeof window !== 'undefined') {
      const handleViewportResize = () => {
        syncViewportWidth();
      };
      window.addEventListener('resize', handleViewportResize);
      viewportResizeCleanup = () => window.removeEventListener('resize', handleViewportResize);
    }

    let motionListenerCleanup: (() => void) | null = null;
    if (typeof window !== 'undefined' && 'matchMedia' in window) {
      const motionQuery = window.matchMedia(PREFERS_REDUCED_MOTION_QUERY);
      prefersReducedMotion = motionQuery.matches;
      const handleMotionChange = (event: MediaQueryListEvent) => {
        prefersReducedMotion = event.matches;
      };
      if ('addEventListener' in motionQuery) {
        motionQuery.addEventListener('change', handleMotionChange);
        motionListenerCleanup = () => motionQuery.removeEventListener('change', handleMotionChange);
      } else {
        motionQuery.addListener(handleMotionChange);
        motionListenerCleanup = () => motionQuery.removeListener(handleMotionChange);
      }
    }

    return () => {
      clearInterval(interval);
      if (resizeObserver) resizeObserver.disconnect();
      if (viewportResizeCleanup) viewportResizeCleanup();
      if (motionListenerCleanup) motionListenerCleanup();
      cancelDragFrame();
      if (separatorEl && activePointerId !== null && separatorEl.hasPointerCapture(activePointerId)) {
        separatorEl.releasePointerCapture(activePointerId);
      }
      activePointerId = null;
      isDragging = false;
    };
  });

  afterUpdate(() => {
    if (typeof window === 'undefined') return;
    syncViewportWidth();
  });

  onDestroy(() => {
    unsubscribeViewport();
  });

  function percentDone() {
    if (tasks.length === 0) return 0;
    return Math.round((tasks.filter((t) => t.done).length / tasks.length) * 100);
  }

  function handleEvidenceCapture(event: CustomEvent<{ payload: EvidenceCapturePayload }>) {
    const payload = event.detail.payload;
    evidence = [
      ...evidence,
      { id: 'e' + (evidence.length + 1), text: payload.text, start: payload.start, end: payload.end, pageId: payload.pageId }
    ];
    const ht = tasks.find((t) => t.type === 'highlight');
    if (ht) ht.done = true;
  }

  function handleHeading(event: CustomEvent<{ heading: ReadingSection | null }>) {
    currentSection = event.detail.heading ?? null;
  }

  function handlePageChange(event: CustomEvent<{ pageId: string }>) {
    currentPageId = event.detail.pageId;
  }

  function setAnswer(id: string, val: string) {
    const trimmed = (val ?? '').trim();
    tasks = tasks.map((task) =>
      task.id === id ? { ...task, answer: val, done: trimmed.length > 3 } : task
    );
  }

  function handleTaskInput(id: string, event: Event) {
    const target = event.target as HTMLTextAreaElement | null;
    setAnswer(id, target?.value ?? '');
  }

  function cancelDragFrame() {
    if (dragFrame !== null && typeof cancelAnimationFrame === 'function') {
      cancelAnimationFrame(dragFrame);
    }
    dragFrame = null;
  }

  function applyContainerMetrics(width: number) {
    containerWidth = width;
    isSingleColumn = width < BREAKPOINT || width <= MIN_PX * 2;
  }

  function setLeftByPx(px: number, width = containerWidth) {
    if (!width || width <= MIN_PX * 2) return;
    const safePx = clampColumnPx(px, width);
    const ratio = pxToFraction(safePx, width);
    leftWidth = ratio;
    rightWidth = 1 - ratio;
  }

  function adjustWidthBy(deltaPx: number) {
    const width = containerWidth;
    if (!width || width <= MIN_PX * 2) return;
    const nextFraction = applyKeyboardResize(normalizedLeft, width, deltaPx);
    leftWidth = nextFraction;
    rightWidth = 1 - nextFraction;
  }

  function updateFromClientX(clientX: number) {
    if (!studentGridEl) return;
    const rect = studentGridEl.getBoundingClientRect();
    const width = rect.width;
    if (!width || width <= MIN_PX * 2) return;
    applyContainerMetrics(width);
    const raw = clientX - rect.left;
    const safe = clampColumnPx(raw, width);
    setLeftByPx(safe, width);
  }

  function schedulePointerUpdate(clientX: number) {
    if (prefersReducedMotion || typeof requestAnimationFrame !== 'function') {
      updateFromClientX(clientX);
      return;
    }
    cancelDragFrame();
    dragFrame = requestAnimationFrame(() => {
      dragFrame = null;
      updateFromClientX(clientX);
    });
  }

  function onPointerDown(event: PointerEvent) {
    if (isSingleColumn) return;
    event.preventDefault();
    activePointerId = event.pointerId;
    isDragging = true;
    separatorEl?.setPointerCapture(activePointerId);
    schedulePointerUpdate(event.clientX);
  }

  function onPointerMove(event: PointerEvent) {
    if (!isDragging || event.pointerId !== activePointerId) return;
    schedulePointerUpdate(event.clientX);
  }

  function onPointerUp(event: PointerEvent) {
    if (!isDragging || event.pointerId !== activePointerId) return;
    schedulePointerUpdate(event.clientX);
    if (separatorEl?.hasPointerCapture(activePointerId)) {
      separatorEl.releasePointerCapture(activePointerId);
    }
    isDragging = false;
    activePointerId = null;
    cancelDragFrame();
  }

  function onLostPointerCapture() {
    isDragging = false;
    activePointerId = null;
    cancelDragFrame();
  }

  function onHandleKeydown(event: KeyboardEvent) {
    if (isSingleColumn) return;
    if (!containerWidth || containerWidth <= MIN_PX * 2) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      const delta = event.key === 'ArrowLeft' ? -KEYBOARD_STEP : KEYBOARD_STEP;
      adjustWidthBy(delta);
    } else if (event.key === 'Home') {
      event.preventDefault();
      setLeftByPx(MIN_PX);
    } else if (event.key === 'End') {
      event.preventDefault();
      setLeftByPx(containerWidth - MIN_PX);
    }
  }

  $: if (isSingleColumn) {
    cancelDragFrame();
    if (separatorEl && activePointerId !== null && separatorEl.hasPointerCapture(activePointerId)) {
      separatorEl.releasePointerCapture(activePointerId);
    }
    activePointerId = null;
    isDragging = false;
  }

  $: totalRatio = leftWidth + rightWidth || 1;
  $: normalizedLeft = totalRatio === 0 ? 0.5 : leftWidth / totalRatio;
  $: normalizedRight = totalRatio === 0 ? 0.5 : rightWidth / totalRatio;
  $: gridTemplate = isSingleColumn
    ? 'minmax(0, 1fr)'
    : `minmax(${MIN_PX}px, ${normalizedLeft}fr) minmax(${MIN_PX}px, ${normalizedRight}fr)`;
  $: effectiveWidth = containerWidth > 0 ? containerWidth : MIN_PX * 2;
  $: currentLeftPx = fractionToPx(normalizedLeft, effectiveWidth);
  $: ariaValueNow = Math.round(clampColumnPx(currentLeftPx, effectiveWidth));
  $: ariaValueMax = effectiveWidth > MIN_PX * 2 ? Math.round(effectiveWidth - MIN_PX) : MIN_PX;
  $: handlePosition = `${normalizedLeft * 100}%`;
  $: progressPercent = percentDone();
  $: progressDashOffset = PROGRESS_RING_CIRCUMFERENCE - (progressPercent / 100) * PROGRESS_RING_CIRCUMFERENCE;
  $: chapterBreadcrumb = { id: 'chapter', label: title, href: '#chapter' };
  $: sectionBreadcrumb = {
    id: 'section',
    label: resolveSectionLabel(currentSection, title),
    href: '#section',
    isCurrent: true
  };
  $: breadcrumbTrail = [COURSE_BREADCRUMB, UNIT_BREADCRUMB, chapterBreadcrumb, sectionBreadcrumb];
  $: isMobileBreadcrumb = isMobileWidth(viewportWidth);
  $: visibleBreadcrumbTrail = isMobileBreadcrumb && breadcrumbTrail.length > 2
    ? breadcrumbTrail.slice(-2)
    : breadcrumbTrail;
  $: hiddenBreadcrumbTrail = isMobileBreadcrumb && breadcrumbTrail.length > visibleBreadcrumbTrail.length
    ? breadcrumbTrail.slice(0, breadcrumbTrail.length - visibleBreadcrumbTrail.length)
    : [];
  $: breadcrumbAriaLabel = `Course navigation: ${breadcrumbTrail.map((crumb) => crumb.label).join(BREADCRUMB_SEPARATOR)}`;
  $: hiddenBreadcrumbLabel = hiddenBreadcrumbTrail.map((crumb) => crumb.label).join(BREADCRUMB_SEPARATOR);

  // ---------- Teacher data ----------
  let rows: StudentRow[] = [
    { name: 'Alice W.', time: '15m', tasks: '7/7', quality: 'Strong' },
    { name: 'Ben R.', time: '9m', tasks: '5/7', quality: 'Weak' },
    { name: 'Chris T.', time: '14m', tasks: '6/7', quality: 'Medium' }
  ];
  let selected: StudentRow | null = null;
  let dialogTriggerEl: HTMLElement | null = null;
  let closeButtonEl: HTMLButtonElement | null = null;
  let dialogContainerEl: HTMLDivElement | null = null;
  let pageContentEl: HTMLDivElement | null = null;
  const dialogTitleId = 'student-drilldown-title';

  function openStudent(row: StudentRow, trigger: HTMLElement | null = null) {
    dialogTriggerEl = trigger;
    selected = row;
  }

  async function focusDialog() {
    await tick();
    if (!selected) return;
    if (closeButtonEl) {
      closeButtonEl.focus();
      return;
    }
    const fallback = dialogContainerEl?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    fallback?.focus();
  }

  async function closeStudent() {
    if (!selected) return;
    selected = null;
    const trigger = dialogTriggerEl;
    await tick();
    trigger?.focus();
    dialogTriggerEl = null;
  }

  function handleDialogKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      closeStudent();
    }
  }

  // -------- Premium & Skim controls --------
  let featureFlags = { premium: false };
  let skimEnabled: boolean = false; // UI toggle (only meaningful if premium)
  let skimThresh = { minDwellMs: 8000, minInteractions: 1, graceRatio: 0.3 };

  // Reactive: auto-seed a DEMO flag when Premium+Skim enabled and no flags exist
  $: if (featureFlags.premium && skimEnabled) {
    if (!rows.some(r => r.flags)) {
      rows = rows.map(r => r.name === 'Ben R.' ? { ...r, flags: 'Possible skim', flagsDemo: true } : r);
    }
  }

  // Reactive: auto-clear only DEMO flags when Skim disabled or Premium off
  $: if (!featureFlags.premium || !skimEnabled) {
    rows = rows.map(r => r.flagsDemo ? ({ ...r, flags: undefined, flagsDemo: undefined }) : r);
  }

  // DEV helpers: seed/clear REAL flags (persist regardless of premium/skim toggles)
  function seedRealFlag(name: string, label = 'Skim (real)') {
    rows = rows.map(r => r.name === name ? ({ ...r, flags: label, flagsDemo: false }) : r);
  }
  function clearRealFlags() {
    rows = rows.map(r => r.flagsDemo ? r : ({ ...r, flags: undefined }));
  }

  $: if (pageContentEl) {
    if (selected) {
      pageContentEl.setAttribute('inert', '');
      pageContentEl.setAttribute('aria-hidden', 'true');
      focusDialog();
    } else {
      pageContentEl.removeAttribute('inert');
      pageContentEl.removeAttribute('aria-hidden');
    }
  }
</script>

<style>
  /* Use :global for truly global selectors inside a component */
  :global(body) { background: #0b1020; color: #e6e9ef; margin: 0; }

  .wrap { padding: 24px; max-width: 1200px; margin: 0 auto; }
  .page-header { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
  .page-header__top { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .page-header__bottom { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  .page-title { margin: 0; flex: 1 1 auto; min-width: 0; }
  .breadcrumb { flex: 1 1 auto; min-width: 0; }
  .breadcrumb__list { display: flex; align-items: center; list-style: none; margin: 0; padding: 0; overflow: hidden; }
  .breadcrumb__item { display: flex; align-items: center; min-width: 0; }
  .breadcrumb__item + .breadcrumb__item::before { content: '›'; color: #5c6578; margin: 0 8px; }
  .breadcrumb__link { background: none; border: none; color: #e6e9ef; font: inherit; text-decoration: none; padding: 4px 0; cursor: pointer; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-flex; align-items: center; gap: 4px; }
  .breadcrumb__link:hover, .breadcrumb__link:focus { text-decoration: underline; }
  .breadcrumb__link:focus-visible { outline: 2px solid #7c9cff; outline-offset: 2px; }
  .breadcrumb__link--current { font-weight: 600; }
  .breadcrumb__item--overflow > .breadcrumb__link { width: 2.25rem; justify-content: center; }
  .breadcrumb__link--overflow { font-size: 1.25rem; line-height: 1; }
  .toggle-label { display: flex; align-items: center; gap: 4px; }
  .progress-ring { position: relative; width: 64px; height: 64px; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .progress-ring__svg { width: 100%; height: 100%; transform: rotate(-90deg); }
  .progress-ring__circle { fill: none; stroke-linecap: round; }
  .progress-ring__circle--bg { stroke: rgba(230, 233, 239, 0.2); }
  .progress-ring__circle--value { stroke: #3ddc97; transition: stroke-dashoffset 0.3s ease; }
  .progress-ring__value { position: absolute; font-size: 0.875rem; font-weight: 600; }
  @media (max-width: 720px) {
    .page-header__top { align-items: flex-start; }
    .breadcrumb__link { max-width: 140px; }
    .progress-ring { width: 56px; height: 56px; }
  }
  .card { background: #0f1428; border-radius: 16px; padding: 16px; }
  .grid { display:grid; gap:16px; }
  .student-grid { position: relative; align-items: start; }
  .student-grid.single-column { grid-template-columns: minmax(0, 1fr); }
  .student-grid.single-column .separator-handle { display: none; }
  .title { font-size: 1.25rem; font-weight: 700; }
  .muted { color: #9aa3b2; }
  .btn {
    background: #7c9cff;
    color: #0b1020;
    border: none;
    padding: 12px 16px;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
    min-height: 44px;
    min-width: 44px;
    line-height: 1.2;
  }

  button.btn,
  a.btn,
  .btn[role='button'] {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .btn.secondary { background: rgba(255,255,255,.08); color: #e6e9ef; }
  .pill { display:inline-block; padding: 2px 8px; border-radius:999px; background: rgba(255,255,255,.06); font-size:12px; }
  .table { width:100%; border-collapse: collapse; }
  .table th, .table td { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 8px; text-align: left; }
  .right { display:flex; align-items:center; justify-content:flex-end; gap: 8px; flex-wrap: wrap; }
  .drawer { max-height: calc(100vh - 64px); overflow:auto; position: sticky; top: 24px; }
  .hl { background: rgba(124,156,255,.18); border-left: 3px solid #7c9cff; padding: 8px; border-radius: 8px; margin: 8px 0; }
  .progress { height: 10px; background: rgba(255,255,255,.08); border-radius: 999px; overflow: hidden; }
  .bar { height: 100%; background: #3ddc97; width: 0%; transition: width .3s ease; }
  .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; }
  .modal { width: 900px; max-width: 95vw; }
  .separator-handle { position: absolute; top: 0; bottom: 0; width: 12px; padding: 0 6px; left: 50%; transform: translateX(-50%); cursor: col-resize; display: flex; align-items: center; justify-content: center; touch-action: none; border-radius: 999px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.08); box-sizing: content-box; }
  .separator-handle:focus { outline: none; }
  .separator-handle:focus-visible { outline: 4px solid #7c9cff; outline-offset: 2px; box-shadow: 0 0 0 4px rgba(124,156,255,0.35); }
  .separator-handle:active { background: rgba(124,156,255,0.25); }
  .separator-grip { width: 2px; height: 48px; background: rgba(255,255,255,0.4); border-radius: 999px; }
</style>

<div class="wrap">
  <div bind:this={pageContentEl}>
    <header class="page-header">
    <div class="page-header__top">
      <nav class="breadcrumb" aria-label={breadcrumbAriaLabel}>
        <ol class="breadcrumb__list">
          {#if hiddenBreadcrumbTrail.length}
            <li class="breadcrumb__item breadcrumb__item--overflow">
              <button
                type="button"
                class="breadcrumb__link breadcrumb__link--overflow"
                aria-label={`Previous levels: ${hiddenBreadcrumbLabel}`}
                title={hiddenBreadcrumbLabel}
              >
                …
              </button>
            </li>
          {/if}
          {#each visibleBreadcrumbTrail as crumb (crumb.id)}
            <li class="breadcrumb__item">
              <a
                class={`breadcrumb__link${crumb.isCurrent ? ' breadcrumb__link--current' : ''}`}
                href={crumb.href}
                aria-current={crumb.isCurrent ? 'page' : undefined}
                title={crumb.label}
              >
                {crumb.label}
              </a>
            </li>
          {/each}
        </ol>
      </nav>
      <div
        class="progress-ring"
        role="img"
        aria-label={`Session progress: ${progressPercent}% complete`}
      >
        <svg
          class="progress-ring__svg"
          viewBox={`0 0 ${PROGRESS_RING_DIAMETER} ${PROGRESS_RING_DIAMETER}`}
          aria-hidden="true"
        >
          <circle
            class="progress-ring__circle progress-ring__circle--bg"
            cx={PROGRESS_RING_DIAMETER / 2}
            cy={PROGRESS_RING_DIAMETER / 2}
            r={PROGRESS_RING_RADIUS}
            stroke-width={PROGRESS_RING_STROKE}
          />
          <circle
            class="progress-ring__circle progress-ring__circle--value"
            cx={PROGRESS_RING_DIAMETER / 2}
            cy={PROGRESS_RING_DIAMETER / 2}
            r={PROGRESS_RING_RADIUS}
            stroke-width={PROGRESS_RING_STROKE}
            stroke-dasharray={`${PROGRESS_RING_CIRCUMFERENCE} ${PROGRESS_RING_CIRCUMFERENCE}`}
            stroke-dashoffset={progressDashOffset}
          />
        </svg>
        <span class="progress-ring__value">{progressPercent}%</span>
      </div>
    </div>
    <div class="page-header__bottom">
      <h1 class="title page-title">Proof‑of‑Reading LMS (Wireframes)</h1>

      <div class="right">
        <label class="toggle-label">
          <input type="checkbox" bind:checked={featureFlags.premium} /> Premium Mode
        </label>
        <label class="toggle-label">
          <input type="checkbox" bind:checked={skimEnabled} disabled={!featureFlags.premium} /> Skim Alerts
        </label>

        <!-- DEV buttons to simulate non-demo flags -->
        <button class="btn secondary" on:click={() => seedRealFlag('Chris T.', 'Skim (real)')}>DEV: Seed Real Flag (Chris)</button>
        <button class="btn secondary" on:click={clearRealFlags}>DEV: Clear Real Flags</button>

        <button class="btn secondary" on:click={() => screen='student'}>Student View</button>
        <button class="btn" on:click={() => screen='teacher'}>Teacher Dashboard</button>
      </div>
    </div>
    </header>

    {#if screen==='student'}
    <!-- Student: Interactive Reader -->
    <div
      class="grid student-grid"
      class:single-column={isSingleColumn}
      bind:this={studentGridEl}
      data-testid="student-grid"
      style={`grid-template-columns:${gridTemplate}`}
    >
      <main class="card" id="student-reading-pane">
        <div class="title" style="margin-bottom:4px;">{title}</div>
        <div class="muted" style="margin-bottom:12px;">Read naturally; complete tasks as you go. Highlights count as evidence.</div>

        <div class="muted" style="margin-bottom:12px;">
          Current section: {currentSection?.title ?? '—'}
          {#if currentPageId}
            <span class="pill" style="margin-left:8px;">Page {currentPageId}</span>
          {/if}
        </div>

        <EpubReader
          pages={samplePages}
          toc={sampleToc}
          landmarks={sampleLandmarks}
          initialPageId={samplePages[0]?.id}
          on:evidencecapture={handleEvidenceCapture}
          on:heading={handleHeading}
          on:pagechange={handlePageChange}
        />

        <div style="margin-top:16px;">
          <div class="muted" style="margin-bottom:6px;">Your evidence</div>
          {#if evidence.length===0}
            <div class="muted">No highlights yet. Use the EPUB reader to highlight text.</div>
          {:else}
            {#each evidence as ev}
              <div class="hl">“{ev.text}” <span class="pill">Pg {ev.pageId}</span> <span class="pill">{ev.start}–{ev.end}</span></div>
            {/each}
          {/if}
        </div>
      </main>

      {#if !isSingleColumn}
        <div
          class="separator-handle"
          bind:this={separatorEl}
          role="separator"
          aria-label="Resize reading and tasks panels"
          aria-controls="student-reading-pane student-tasks-pane"
          aria-orientation="vertical"
          aria-valuemin={MIN_PX}
          aria-valuemax={ariaValueMax}
          aria-valuenow={ariaValueNow}
          tabindex="0"
          style={`left:${handlePosition}`}
          on:pointerdown={onPointerDown}
          on:pointermove={onPointerMove}
          on:pointerup={onPointerUp}
          on:pointercancel={onPointerUp}
          on:lostpointercapture={onLostPointerCapture}
          on:keydown={onHandleKeydown}
        >
          <span class="separator-grip" aria-hidden="true"></span>
        </div>
      {/if}

      <aside class="card drawer" id="student-tasks-pane" aria-label="Tasks panel">
        <div class="title" style="margin-bottom:8px;">Tasks</div>
        <div class="muted" style="margin-bottom:8px;">Progress</div>
        <div class="progress"><div class="bar" style={`width:${progressPercent}%`}></div></div>
        <div class="muted" style="margin:8px 0 16px 0;">{tasks.filter(t=>t.done).length}/{tasks.length} completed • {Math.floor(dwellMs/60_000)}m spent</div>

        <!-- Task list -->
        {#each tasks as t}
          <div class="card" style="margin-bottom:10px;">
            <div style="font-weight:600;">{t.prompt}</div>
            {#if t.type==='highlight'}
              <div class="muted" style="font-size:12px;">Select a sentence in the reading to complete.</div>
              {#if t.done}<div class="pill" style="margin-top:6px;background:rgba(61,220,151,.18); color: #3ddc97;">Completed</div>{/if}
            {:else}
              <textarea
                class="card"
                rows="3"
                placeholder="Type your response…"
                on:input={(event) => handleTaskInput(t.id, event)}
              >{t.answer || ''}</textarea>
            {/if}
          </div>
        {/each}

        <button class="btn" style="width:100%; margin-top:8px;">Submit All Evidence & Answers</button>
      </aside>
    </div>
    {/if}

    {#if screen==='teacher'}
    <!-- Premium Settings (Skim Alerts) -->
    {#if featureFlags.premium}
      <section class="card" style="margin-bottom:16px;">
        <div class="title">Premium • Skim Alerts</div>
        <label style="display:flex;align-items:center;gap:8px;margin:8px 0;">
          <input type="checkbox" bind:checked={skimEnabled} />
          Enable skim alerts (time-on-section + few interactions)
        </label>
        {#if skimEnabled}
          <div style="display:flex; gap:12px;">
            <label style="flex:1">Min dwell per bin (ms)
              <input class="btn secondary" type="number" min="0" bind:value={skimThresh.minDwellMs} />
            </label>
            <label style="flex:1">Min interactions per bin
              <input class="btn secondary" type="number" min="0" bind:value={skimThresh.minInteractions} />
            </label>
            <label style="flex:1">Grace ratio (0–1)
              <input class="btn secondary" type="number" min="0" max="1" step="0.05" bind:value={skimThresh.graceRatio} />
            </label>
          </div>
          <div class="muted" style="margin-top:6px;font-size:12px;">We never block submissions. Alerts are suggestions for teacher review only.</div>
        {/if}
      </section>
    {:else}
      <section class="card" style="margin-bottom:16px;">
        <div class="title">Skim Alerts</div>
        <div class="muted">Flag possible skimming using low time-on-section and missing evidence.</div>
        <div class="muted" style="margin-top:6px;">Unlock with Premium to configure thresholds and see alerts.</div>
      </section>
    {/if}

    <QuestionPanel />

    <section class="card" style="margin-top:16px;">
      <div class="title" style="margin-bottom:8px;">Student Evidence Table</div>
      <table class="table">
        <thead>
          <tr><th>Name</th><th>Time</th><th>Tasks Done</th><th>Evidence Quality</th><th>Flags</th><th></th></tr>
        </thead>
        <tbody>
          {#each rows as r}
            <tr>
              <td>{r.name}</td>
              <td>{r.time}</td>
              <td>{r.tasks}</td>
              <td>{r.quality}</td>
              <td>
                {#if r.flags}
                  <span class="pill" style="background:rgba(255,209,102,.18); color: #ffd166;" title="Possible skim: flagged when dwell time and interactions fall below thresholds. Click to review details.">{r.flags}{r.flagsDemo ? ' (demo)' : ''}</span>
                {:else}
                  —
                {/if}
              </td>
              <td>
                <button
                  class="btn secondary"
                  type="button"
                  on:click={(event) => openStudent(r, event.currentTarget as HTMLElement)}
                >
                  View
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      <div class="muted" style="margin-top:8px;font-size:12px;">
        {#if featureFlags.premium && skimEnabled}
          <span class="pill" style="background:rgba(255,209,102,.18); color: #ffd166;">Possible skim</span> = flagged when dwell time and interactions fall below thresholds. Demo flags auto-clear; real flags persist.
        {/if}
      </div>
    </section>

    {/if}

  </div>

  {#if screen==='teacher' && selected}
    <!-- Make overlay keyboard-accessible -->
    <div
      class="overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby={dialogTitleId}
      on:click={closeStudent}
      on:keydown={handleDialogKeydown}
    >
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <div class="card modal" bind:this={dialogContainerEl} on:click|stopPropagation>
        <div style="display:flex;align-items:center;justify-content:space-between; margin-bottom:8px;">
          <div class="title" id={dialogTitleId}>{selected.name} — Evidence Drilldown</div>
          <button class="btn secondary" type="button" bind:this={closeButtonEl} on:click={closeStudent}>Close</button>
        </div>

        <div class="grid two">
          <div class="card">
            <div class="muted" style="margin-bottom:8px;">Reading with highlights (mock)</div>
            <div class="hl">“failed harvest … rationing policy” <span class="pill">evidence</span></div>
            <div class="hl">“Rumors of favoritism … audits later contradicted” <span class="pill">evidence</span></div>
          </div>

          <div class="card">
            <div class="muted">Submitted answers</div>
            <div class="card" style="margin-top:8px;">
              <div style="font-weight:600;">Q1</div>
              <div class="muted">Short answer: “Because the harvest failed and supplies ran low.”</div>
            </div>
            <div class="card" style="margin-top:8px;">
              <div style="font-weight:600;">Q2</div>
              <div class="muted">Summary: “The policy aimed to allocate flour fairly, though people feared favoritism.”</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
