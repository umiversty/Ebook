<script lang="ts">
  export let chips: { text: string; ariaLabel: string; value: string }[] = [];
  export let onBloomChipClick: (value: string, target: HTMLElement) => void = () => {};

  function handleChipClick(event: Event, value: string) {
    const target = event.currentTarget as HTMLButtonElement;
    onBloomChipClick(value, target);
  }

  function handleBloomChipEvent(value: BloomChipValue, event: Event) {
    onBloomChipClick(value, event.currentTarget as HTMLButtonElement | null);
  }

  function handleDifficultyChipEvent(value: DifficultyChipValue, event: Event) {
    onDifficultyChipClick(value, event.currentTarget as HTMLButtonElement | null);
  }
</script>

<div class="chip-panel">
  {#each chips as chip}
    <button
      aria-label={chip.ariaLabel}
      on:click={(e) => handleChipClick(e, chip.value)}
    >
<<<<<<< HEAD
      {chip.text}
    </button>
=======
      {#if $selectedTabId === tab.id}
        <p class="tab-description">{tab.description}</p>

        <div class="filters">
          <div class="filter-group">
            <span class="filter-label">Bloom tier</span>
            <div class="chip-row">
              {#each bloomChips as chip}
                <button
                  type="button"
                  class="chip"
                  class:active={$bloomFilter === chip.value}
                  aria-pressed={$bloomFilter === chip.value}
                  aria-label={chip.ariaLabel}
                  on:click={(event) => handleBloomChipEvent(chip.value, event)}
                >
                  {chip.text}
                </button>
              {/each}
            </div>
          </div>
          <div class="filter-group">
            <span class="filter-label">Difficulty</span>
            <div class="chip-row">
              {#each difficultyChips as chip}
                <button
                  type="button"
                  class="chip"
                  class:active={$difficultyFilter === chip.value}
                  aria-pressed={$difficultyFilter === chip.value}
                  aria-label={chip.ariaLabel}
                  on:click={(event) => handleDifficultyChipEvent(chip.value, event)}
                >
                  {chip.text}
                </button>
              {/each}
            </div>
          </div>
        </div>

        <ul class="question-list" aria-label={`${tab.label} questions`} aria-live="polite">
          {#if $filteredQuestions.length > 0}
            {#each $filteredQuestions as question (question.id)}
              <li class="question-item">
                <h3 class="question-title">{question.prompt}</h3>
                <div class="question-meta">
                  <span class="chip meta" aria-label={`Bloom tier ${question.bloom}`}>{question.bloom}</span>
                  <span class="chip meta" aria-label={`Difficulty ${question.difficulty}`}>
                    {question.difficulty}
                  </span>
                  <span class="meta-label">{question.focus}</span>
                  {#if question.responseGuide}
                    <span class="meta-label">Guide: {question.responseGuide}</span>
                  {/if}
                </div>
                <section
                  class="question-location"
                  aria-labelledby={`${question.id}-location-heading`}
                >
                  <h4 id={`${question.id}-location-heading`} class="location-heading">
                    Source location
                  </h4>
                  <dl class="location-list">
                    <div class="location-row">
                      <dt class="location-term">Section</dt>
                      <dd class="location-definition">
                        <span class="location-section">{question.readingSection.title}</span>
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
              </li>
            {/each}
          {:else}
            <li class="question-empty">No questions match the selected filters.</li>
          {/if}
        </ul>
      {/if}
    </div>
>>>>>>> 32cc9799d8353706474bd002ae1b2e8bb8e5042a
  {/each}
</div>

<style>
  .chip-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  button {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: 1px solid #ccc;
    background: #f5f5f5;
    cursor: pointer;
  }
</style>
