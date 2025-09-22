<script lang="ts">
  // A single question card panel

  export let q: {
    id: string;
    stem: string;
    hint?: string;
    answer?: string;
    location?: {
      section?: string;
      page?: number;
      offsets?: [number, number];
      snippet?: string;
    };
  };

  // Whether this panel’s accordion is expanded
  export let expanded: boolean = false;

  // Callback provided by parent to toggle accordion state
  export let toggleHint: (id: string) => void = () => {};

  let answerExpanded = false;

  const toggleAnswer = () => {
    answerExpanded = !answerExpanded;
  };

  const handleToggleKeydown = (event: KeyboardEvent, toggle: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle();
    }
  };
</script>

<article class="question-card" aria-labelledby={`question-${q.id}-stem`}>
  <header class="question-header">
    <h2 class="question-stem" id={`question-${q.id}-stem`}>
      {q.stem}
    </h2>
  </header>

  {#if q.hint?.trim()}
    <section class="hint-section">
      <h3 class="hint-heading" id={`question-${q.id}-hint-heading`}>
        <button
          type="button"
          class="hint-toggle"
          aria-controls={`hint-${q.id}`}
          aria-expanded={expanded}
          on:click={() => toggleHint(q.id)}
          on:keydown={(event) =>
            handleToggleKeydown(event, () => toggleHint(q.id))}
        >
          {expanded ? 'Hide hint' : 'Show hint'}
        </button>
      </h3>

      {#if expanded}
        <div
          id={`hint-${q.id}`}
          role="region"
          aria-labelledby={`question-${q.id}-hint-heading`}
          class="hint-panel"
        >
          <p>{q.hint}</p>
        </div>
      {/if}
    </section>
  {/if}

  {#if q.answer?.trim()}
    <section class="answer-section">
      <h3 class="answer-heading" id={`question-${q.id}-answer-heading`}>
        <button
          type="button"
          class="answer-toggle"
          aria-controls={`answer-${q.id}`}
          aria-expanded={answerExpanded}
          on:click={toggleAnswer}
          on:keydown={(event) => handleToggleKeydown(event, toggleAnswer)}
        >
          {answerExpanded ? 'Hide answer' : 'Show answer'}
        </button>
      </h3>

      {#if answerExpanded}
        <div
          id={`answer-${q.id}`}
          role="region"
          aria-labelledby={`question-${q.id}-answer-heading`}
          class="answer-panel"
        >
          <p>{q.answer}</p>
        </div>
      {/if}
    </section>
  {/if}

  {#if q.location}
    <section class="location-section" aria-labelledby={`question-${q.id}-location-heading`}>
      <h3 class="location-heading" id={`question-${q.id}-location-heading`}>
        Source location
      </h3>
      <dl class="location-list">
          {#if q.location.section}
            <div class="location-row">
              <dt class="location-term">Section</dt>
              <dd><span class="location-section-title">{q.location.section}</span></dd>
            </div>
          {/if}
          {#if q.location.page}
            <div class="location-row">
              <dt class="location-term">Page</dt>
              <dd>{q.location.page}</dd>
            </div>
          {/if}
          {#if q.location.offsets}
            <div class="location-row">
              <dt class="location-term">Offsets</dt>
              <dd>{q.location.offsets[0]} – {q.location.offsets[1]}</dd>
            </div>
        {/if}
      </dl>

      {#if q.location.snippet}
        <p class="location-snippet" aria-label="Referenced text">
          “{q.location.snippet}”
        </p>
      {/if}
    </section>
  {/if}
</article>

<style>
  .question-card { background:#0f1428; padding:16px; border-radius:12px; margin-bottom:12px; }
  .question-stem { font-size:1.1rem; font-weight:600; }
  .hint-toggle, .answer-toggle {
    background:none; border:none; color:#7c9cff;
    cursor:pointer; font-weight:600;
  }
  .hint-heading, .location-heading { font-size:1rem; margin-top:12px; }
  .location-list { margin:0; padding:0; }
  .location-row { display:flex; gap:8px; }
  .location-term { font-weight:600; }
  .location-snippet { font-style:italic; margin-top:6px; }
</style>
