<script lang="ts">
  import EpubReader from './src/lib/epub/EpubReader.svelte';
  import { sampleLandmarks, samplePages, sampleToc } from './src/lib/epub/sampleData.js';
  import type { EpubHeading, EvidenceCapturePayload } from './src/lib/epub/types.js';
  import { applyKeyboardResize, clampColumnPx, fractionToPx, MIN_COLUMN_PX, pxToFraction } from './splitLayout';
  import { onMount, tick } from 'svelte';
  import QuestionPanel from './src/lib/teacher/QuestionPanel.svelte';

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
  let currentHeading: EpubHeading | null = samplePages[0]?.headings[0] ?? null;
  let currentPageId: string | null = samplePages[0]?.id ?? null;
  let dwellMs = 0;
  let viewportWidth = typeof window !== 'undefined' ? window.innerWidth : BREAKPOINT;

  // -------- Breadcrumbs --------
  type BreadcrumbNode = { id: string; label: string; href: string; isCurrent?: boolean };
  const COURSE_BREADCRUMB: BreadcrumbNode = { id: 'course', label: 'AP U.S. History', href: '#course' };
  const UNIT_BREADCRUMB: BreadcrumbNode = { id: 'unit', label: 'Unit 7 · Domestic Impacts', href: '#unit' };
  const PROGRESS_RING_RADIUS = 20;
  const PROGRESS_RING_STROKE = 4;
  const PROGRESS_RING_DIAMETER = PROGRESS_RING_RADIUS * 2 + PROGRESS_RING_STROKE * 2;
  const PROGRESS_RING_CIRCUMFERENCE = 2 * Math.PI * PROGRESS_RING_RADIUS;
  const BREADCRUMB_SEPARATOR = ' › ';

  let chapterBreadcrumb: BreadcrumbNode = { id: 'chapter', label: title, href: '#chapter' };
  let sectionBreadcrumb: BreadcrumbNode = {
    id: 'section',
    label: resolveSectionLabel(currentHeading, title),
    href: '#section',
    isCurrent: true
  };

  let breadcrumbTrail: BreadcrumbNode[] = [COURSE_BREADCRUMB, UNIT_BREADCRUMB, chapterBreadcrumb, sectionBreadcrumb];
  let isMobileBreadcrumb = viewportWidth < BREAKPOINT;
  let visibleBreadcrumbTrail: BreadcrumbNode[] = breadcrumbTrail;
  let hiddenBreadcrumbTrail: BreadcrumbNode[] = [];
  let breadcrumbAriaLabel = `Course navigation: ${breadcrumbTrail.map((c) => c.label).join(BREADCRUMB_SEPARATOR)}`;
  let hiddenBreadcrumbLabel = '';

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

  // -------- Premium & Skim controls --------
  let featureFlags = { premium: false };
  let skimEnabled: boolean = false;
  let skimThresh = { minDwellMs: 8000, minInteractions: 1, graceRatio: 0.3 };

  // ---------------- Functions ----------------
  function syncViewportWidth() {
    if (typeof window === 'undefined') return;
    viewportWidth = window.innerWidth;
  }

  function resolveSectionLabel(heading: EpubHeading | null, chapterTitle: string): string {
    if (!heading) return 'Section overview';
    if (heading.text.trim() === chapterTitle.trim()) return 'Overview';
    return heading.text;
  }

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

  function handleHeading(event: CustomEvent<{ heading: EpubHeading | null }>) {
    currentHeading = event.detail.heading ?? null;
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

  function handleInput(e: Event, id: string) {
    const target = e.target as HTMLTextAreaElement;
    setAnswer(id, target.value);
  }

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

  // DEV helpers: seed/clear REAL flags
  function seedRealFlag(name: string, label = 'Skim (real)') {
    rows = rows.map(r => r.name === name ? ({ ...r, flags: label, flagsDemo: false }) : r);
  }
  function clearRealFlags() {
    rows = rows.map(r => r.flagsDemo ? r : ({ ...r, flags: undefined }));
  }

  // ---------------- Lifecycle ----------------
  onMount(() => {
    const interval = setInterval(() => { dwellMs += 1000; }, 1000);
    syncViewportWidth();
    return () => clearInterval(interval);
  });

  // ---------------- Reactive ----------------
  $: progressPercent = percentDone();
  $: progressDashOffset = PROGRESS_RING_CIRCUMFERENCE - (progressPercent / 100) * PROGRESS_RING_CIRCUMFERENCE;
  $: chapterBreadcrumb = { id: 'chapter', label: title, href: '#chapter' };
  $: sectionBreadcrumb = { id: 'section', label: resolveSectionLabel(currentHeading, title), href: '#section', isCurrent: true };
  $: breadcrumbTrail = [COURSE_BREADCRUMB, UNIT_BREADCRUMB, chapterBreadcrumb, sectionBreadcrumb];
  $: isMobileBreadcrumb = viewportWidth < BREAKPOINT;
  $: visibleBreadcrumbTrail = isMobileBreadcrumb && breadcrumbTrail.length > 2 ? breadcrumbTrail.slice(-2) : breadcrumbTrail;
  $: hiddenBreadcrumbTrail = isMobileBreadcrumb && breadcrumbTrail.length > visibleBreadcrumbTrail.length
    ? breadcrumbTrail.slice(0, breadcrumbTrail.length - visibleBreadcrumbTrail.length)
    : [];
  $: breadcrumbAriaLabel = `Course navigation: ${breadcrumbTrail.map((c) => c.label).join(BREADCRUMB_SEPARATOR)}`;
  $: hiddenBreadcrumbLabel = hiddenBreadcrumbTrail.map((c) => c.label).join(BREADCRUMB_SEPARATOR);

  // -------- DEMO flags auto-seed/clear --------
  $: if (featureFlags.premium && skimEnabled) {
    if (!rows.some(r => r.flags)) {
      rows = rows.map(r => r.name === 'Ben R.' ? { ...r, flags: 'Possible skim', flagsDemo: true } : r);
    }
  }
  $: if (!featureFlags.premium || !skimEnabled) {
    rows = rows.map(r => r.flagsDemo ? ({ ...r, flags: undefined, flagsDemo: undefined }) : r);
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

<!-- keep your existing <style> and <div class="wrap"> markup structure -->
