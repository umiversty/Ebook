<script lang="ts">
  export type QuestionLocation = {
    section: string;
    page: number | string;
    offsets: [number, number];
    snippet: string;
  };

  export type GeneratedQuestion = {
    id: string;
    stem: string;
    hint?: string;
    answer?: string;
    whyThisMatters?: string;
    location: QuestionLocation;
  };

  export let q: GeneratedQuestion;
  export let expanded = false;
  export let toggleHint: (questionId: string) => void;

  let hintButtonId: string;
  let hintPanelId: string;

  $: hintButtonId = `${q.id}-hint-toggle`;
  $: hintPanelId = `${q.id}-hint-panel`;

  function setAriaExpanded(target: EventTarget | null, value: boolean) {
    if (target instanceof HTMLElement) {
      target.setAttribute('aria-expanded', value ? 'true' : 'false');
    }
  }

  function announceToggle(event: MouseEvent | KeyboardEvent) {
    const nextExpanded = !expanded;
    setAriaExpanded(event.currentTarget, nextExpanded);
    toggleHint(q.id);
  }

  function handleToggleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      announceToggle(event);
    }
  }
</script>

<article class="question" aria-labelledby={`${q.id}-stem`}>
  <header class="question-header">
    <h3 id={`${q.id}-stem`} class="question-stem">{q.stem}</h3>
    <button
      type="button"
      class="hint-toggle"
      id={hintButtonId}
      aria-controls={hintPanelId}
      aria-expanded={expanded ? 'true' : 'false'}
      on:click={announceToggle}
      on:keydown={handleToggleKeydown}
    >
      {expanded ? 'Hide hint' : 'Show hint'}
    </button>
  </header>

  {#if q.hint}
    <section
      id={hintPanelId}
      class="hint"
      aria-labelledby={hintButtonId}
      aria-hidden={expanded ? 'false' : 'true'}
      hidden={!expanded}
    >
      <p>{q.hint}</p>
      {#if q.answer}
        <p class="answer"><strong>Answer:</strong> {q.answer}</p>
      {/if}
      {#if q.whyThisMatters}
        <p class="supporting">{q.whyThisMatters}</p>
      {/if}
    </section>
  {/if}

  <section class="location" aria-labelledby={`${q.id}-location-heading`}>
    <h4 id={`${q.id}-location-heading`} class="location-heading">Source location</h4>
    <dl class="location-details">
      <div>
        <dt>Section</dt>
        <dd>{q.location.section}</dd>
      </div>
      <div>
        <dt>Page</dt>
        <dd>{q.location.page}</dd>
      </div>
      <div>
        <dt>Offsets</dt>
        <dd>{q.location.offsets[0]}–{q.location.offsets[1]}</dd>
      </div>
    </dl>
    <p class="location-snippet">{q.location.snippet}</p>
  </section>
</article>

<style>
  .question {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(12, 18, 36, 0.75);
    color: #f5f7ff;
  }

  .question-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  .question-stem {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .hint-toggle {
    border: none;
    border-radius: 999px;
    padding: 0.5rem 1rem;
    background: rgba(124, 156, 255, 0.25);
    color: inherit;
    cursor: pointer;
    font-weight: 500;
  }

  .hint-toggle:focus-visible {
    outline: 3px solid rgba(124, 156, 255, 0.6);
    outline-offset: 2px;
  }

  .hint[hidden] {
    display: none;
  }

  .hint {
    margin: 0;
    padding: 1rem;
    border-radius: 12px;
    background: rgba(124, 156, 255, 0.12);
  }

  .location {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .location-heading {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }

  .location-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
    margin: 0;
  }

  .location-details div {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  dt {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(245, 247, 255, 0.6);
  }

  dd {
    margin: 0;
    font-weight: 500;
  }

  .location-snippet {
    margin: 0;
    font-style: italic;
    color: rgba(245, 247, 255, 0.85);
  }
</style>
