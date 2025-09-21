<svelte:options runes={false} />

<script lang="ts">
  import type { ReadingSection, ReadingTextSpan } from '../reading/types';

  export interface GeneratedQuestion {
    id: string;
    stem: string;
    hint?: string;
    answer: string;
    whyThisMatters: string;
    readingSection: ReadingSection;
    textSpan: ReadingTextSpan;
  }

  export let questions: GeneratedQuestion[] = [];

  let openHints = new Set<string>();
  let openAnswers = new Set<string>();

  const toggleSet = (set: Set<string>, id: string): Set<string> => {
    const next = new Set(set);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    return next;
  };

  const toggleHint = (id: string) => {
    openHints = toggleSet(openHints, id);
  };

  const toggleAnswer = (id: string) => {
    openAnswers = toggleSet(openAnswers, id);
  };
</script>

<section class="new-question-panel">
  {#each questions as question (question.id)}
    <article class="question-card" aria-labelledby={`${question.id}-stem`}>
      <header class="question-header">
        <h2 id={`${question.id}-stem`} class="question-stem">{question.stem}</h2>
      </header>

      {#if question.hint?.trim()}
        <section class="hint-section">
          <h3 id={`${question.id}-hint-heading`} class="hint-heading">
            <button
              type="button"
              class="hint-toggle"
              aria-expanded={openHints.has(question.id)}
              aria-controls={`${question.id}-hint-panel`}
              on:click={() => toggleHint(question.id)}
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
        <button
          id={`${question.id}-answer-toggle`}
          type="button"
          class="answer-toggle"
          aria-expanded={openAnswers.has(question.id)}
          aria-controls={`${question.id}-answer-panel`}
          on:click={() => toggleAnswer(question.id)}
        >
          {openAnswers.has(question.id) ? 'Hide answer' : 'Show answer'}
        </button>

        {#if openAnswers.has(question.id)}
          <div
            id={`${question.id}-answer-panel`}
            role="region"
            aria-labelledby={`${question.id}-answer-toggle`}
            class="answer-panel"
          >
            <p>{question.answer}</p>
          </div>
        {/if}
      </section>

      <section
        class="location-section"
        aria-labelledby={`${question.id}-location-heading`}
      >
        <h3 id={`${question.id}-location-heading`} class="location-heading">
          Source location
        </h3>
        <dl class="location-list">
          <div class="location-row">
            <dt class="location-term">Section</dt>
            <dd class="location-definition">
              <span class="location-section-title">{question.readingSection.title}</span>
              <span class="location-chapter">{question.readingSection.chapterTitle}</span>
            </dd>
          </div>
          <div class="location-row">
            <dt class="location-term">Page</dt>
            <dd class="location-definition">{question.readingSection.pageLabel}</dd>
          </div>
          <div class="location-row">
            <dt class="location-term">Offsets</dt>
            <dd class="location-definition">
              {question.textSpan.startOffset}&ndash;{question.textSpan.endOffset}
            </dd>
          </div>
        </dl>
        <p class="location-snippet" aria-label="Referenced text">
          &ldquo;{question.textSpan.text}&rdquo;
        </p>
      </section>

      <section
        class="importance-section"
        aria-labelledby={`${question.id}-importance-heading`}
      >
        <h3 id={`${question.id}-importance-heading`} class="importance-heading">
          Why this matters
        </h3>
        <p class="importance-body">{question.whyThisMatters}</p>
      </section>
    </article>
  {/each}
</section>

<style>
  .new-question-panel {
    display: grid;
    gap: 1.5rem;
  }

  .question-card {
    border: 1px solid var(--panel-border, #d0d7de);
    border-radius: 0.75rem;
    padding: 1.5rem;
    background: var(--panel-surface, #fff);
    box-shadow: var(--panel-shadow, 0 1px 2px rgba(15, 23, 42, 0.08));
  }

  .question-stem {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    line-height: 1.4;
  }

  .hint-heading {
    margin: 0;
  }

  .hint-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    padding: 0.25rem 0.25rem;
    background: none;
    border: none;
    color: inherit;
    text-align: left;
    cursor: pointer;
    border-radius: 0.75rem;
  }

  .answer-toggle {
    margin-top: 1rem;
    font-size: 1rem;
    padding: 0.5rem 0.75rem;
    border-radius: 0.75rem;
  }

  .hint-toggle:focus,
  .answer-toggle:focus {
    outline: none;
  }

  .hint-toggle:focus-visible,
  .answer-toggle:focus-visible {
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.55);
  }

  .answer-panel,
  .hint-panel,
  .importance-section,
  .location-section {
    margin-top: 0.75rem;
  }

  .importance-heading {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
  }

  .importance-body {
    margin: 0;
  }

  .location-section {
    border: 1px solid var(--panel-border, #d0d7de);
    border-radius: 0.75rem;
    padding: 1rem;
    background: var(--panel-surface-alt, #f8fafc);
  }

  .location-heading {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
  }

  .location-list {
    margin: 0 0 0.75rem 0;
    display: grid;
    gap: 0.5rem;
  }

  .location-row {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.75rem;
    align-items: baseline;
    font-size: 0.95rem;
  }

  .location-term {
    font-weight: 600;
  }

  .location-definition {
    margin: 0;
  }

  .location-section-title {
    display: block;
    font-weight: 600;
  }

  .location-chapter {
    display: block;
    font-size: 0.85rem;
    color: #475569;
  }

  .location-snippet {
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.4;
  }
</style>
