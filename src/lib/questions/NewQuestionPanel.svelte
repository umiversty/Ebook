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

<<<<<<< HEAD
  // Callback provided by parent to toggle accordion state
  export let toggleHint: (id: string) => void = () => {};
=======
  const toggleAnswer = (id: string) => {
    openAnswers = toggleSet(openAnswers, id);
  };

  const handleToggleKeydown = (
    event: KeyboardEvent,
    id: string,
    toggle: (itemId: string) => void
  ) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle(id);
    }
  };
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
</script>

<article class="question-card" aria-labelledby={`question-${q.id}-stem`}>
  <header class="question-header">
    <h2 class="question-stem" id={`question-${q.id}-stem`}>
      {q.stem}
    </h2>
  </header>

<<<<<<< HEAD
  {#if q.hint}
    <section class="hint-section">
      <h3 class="hint-heading" id={`question-${q.id}-hint-heading`}>
=======
      {#if question.hint?.trim()}
        <section class="hint-section">
          <h3 id={`${question.id}-hint-heading`} class="hint-heading">
            <button
              type="button"
              class="hint-toggle"
              aria-expanded={openHints.has(question.id)}
              aria-controls={`${question.id}-hint-panel`}
              on:click={() => toggleHint(question.id)}
              on:keydown={(event) => handleToggleKeydown(event, question.id, toggleHint)}
            >
              {openHints.has(question.id) ? 'Hide hint' : 'Show hint'}
            </button>
          </h3>

          {#if openHints.has(question.id)}
            <div
              id={`${question.id}-hint-panel`}
              role="region"
              aria-labelledby={`${question.id}-hint-heading`}
              class="hint-panel"
            >
              <p>{question.hint}</p>
            </div>
          {/if}
        </section>
      {/if}

      <section class="answer-section">
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
        <button
          type="button"
<<<<<<< HEAD
          class="hint-toggle"
          aria-controls={`hint-${q.id}`}
          aria-expanded={expanded}
          on:click={() => toggleHint(q.id)}
=======
          class="answer-toggle"
          aria-expanded={openAnswers.has(question.id)}
          aria-controls={`${question.id}-answer-panel`}
          on:click={() => toggleAnswer(question.id)}
          on:keydown={(event) => handleToggleKeydown(event, question.id, toggleAnswer)}
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
        >
          {expanded ? 'Hide hint' : 'Show hint'}
        </button>
      </h3>

      <div
        id={`hint-${q.id}`}
        hidden={!expanded}
        aria-labelledby={`question-${q.id}-hint-heading`}
      >
        {q.hint}
      </div>
    </section>
  {/if}

  {#if q.answer}
    <section class="answer-section">
      <button
        type="button"
        class="answer-toggle"
        aria-controls={`answer-${q.id}`}
        aria-expanded="false"
      >
        Show answer
      </button>
      <div id={`answer-${q.id}`} hidden>
        {q.answer}
      </div>
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
            <dt>Section</dt>
            <dd><span class="location-section-title">{q.location.section}</span></dd>
          </div>
        {/if}
        {#if q.location.page}
          <div class="location-row">
            <dt>Page</dt>
            <dd>{q.location.page}</dd>
          </div>
        {/if}
        {#if q.location.offsets}
          <div class="location-row">
            <dt>Offsets</dt>
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
