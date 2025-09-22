<script lang="ts">
  import {
    bloomChips,
    createQuestionPanelStores,
    difficultyChips,
    handleTabKey,
    questionTabs,
    tabOrder,
    updateBloomFilter,
    updateDifficultyFilter,
    type BloomFilterValue,
    type DifficultyFilterValue,
    type QuestionPanelStores
  } from './questionPanelState';

  const fallbackStores = createQuestionPanelStores();

  export let stores: QuestionPanelStores | undefined = undefined;
  export let onBloomChipClick:
    | ((value: BloomFilterValue, target: HTMLButtonElement | null) => void)
    | undefined = undefined;
  export let onDifficultyChipClick:
    | ((value: DifficultyFilterValue, target: HTMLButtonElement | null) => void)
    | undefined = undefined;

  let selectedTabIdStore = fallbackStores.selectedTabId;
  let focusedTabIdStore = fallbackStores.focusedTabId;
  let bloomFilterStore = fallbackStores.bloomFilter;
  let difficultyFilterStore = fallbackStores.difficultyFilter;
  let filteredQuestionsStore = fallbackStores.filteredQuestions;

  $: if (stores) {
    selectedTabIdStore = stores.selectedTabId;
    focusedTabIdStore = stores.focusedTabId;
    bloomFilterStore = stores.bloomFilter;
    difficultyFilterStore = stores.difficultyFilter;
    filteredQuestionsStore = stores.filteredQuestions;
  }

  $: bloomChipHandler =
    onBloomChipClick ??
    ((value: BloomFilterValue, target: HTMLButtonElement | null) =>
      updateBloomFilter(bloomFilterStore, value, target));

  $: difficultyChipHandler =
    onDifficultyChipClick ??
    ((value: DifficultyFilterValue, target: HTMLButtonElement | null) =>
      updateDifficultyFilter(difficultyFilterStore, value, target));

  function selectTab(id: string) {
    selectedTabIdStore.set(id);
    focusedTabIdStore.set(id);
  }

  function focusTab(id: string) {
    focusedTabIdStore.set(id);
  }

  function handleTabKeyDown(event: KeyboardEvent, id: string) {
    if (
      handleTabKey(event.key, id, {
        tabOrder,
        focus: focusTab,
        select: selectTab
      })
    ) {
      event.preventDefault();
    }
  }

  function handleBloomChipEvent(value: BloomFilterValue, event: Event) {
    bloomChipHandler(value, event.currentTarget as HTMLButtonElement | null);
  }

  function handleDifficultyChipEvent(value: DifficultyFilterValue, event: Event) {
    difficultyChipHandler(value, event.currentTarget as HTMLButtonElement | null);
  }

  $: activeTab =
    questionTabs.find((tab) => tab.id === $selectedTabIdStore) ?? questionTabs[0];
</script>

<div class="question-panel" role="region" aria-label="Generated questions">
  <div class="tablist" role="tablist" aria-label="Question types">
    {#each questionTabs as tab}
      <button
        id={`question-tab-${tab.id}`}
        type="button"
        role="tab"
        class="tab"
        class:active={$selectedTabIdStore === tab.id}
        aria-selected={$selectedTabIdStore === tab.id}
        aria-controls={`question-panel-${tab.id}`}
        tabindex={$focusedTabIdStore === tab.id ? 0 : -1}
        on:click={() => selectTab(tab.id)}
        on:focus={() => focusTab(tab.id)}
        on:keydown={(event) => handleTabKeyDown(event, tab.id)}
      >
        {tab.label}
      </button>
    {/each}
  </div>

  {#if activeTab}
    <div
      id={`question-panel-${activeTab.id}`}
      class="tabpanel"
      role="tabpanel"
      aria-labelledby={`question-tab-${activeTab.id}`}
      tabindex="0"
    >
      <p class="tab-description">{activeTab.description}</p>

      <div class="filters">
        <div class="filter-group">
          <span class="filter-label">Bloom tier</span>
          <div class="chip-row">
            {#each bloomChips as chip}
              <button
                type="button"
                class="chip"
                class:active={$bloomFilterStore === chip.value}
                aria-pressed={$bloomFilterStore === chip.value}
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
                class:active={$difficultyFilterStore === chip.value}
                aria-pressed={$difficultyFilterStore === chip.value}
                aria-label={chip.ariaLabel}
                on:click={(event) => handleDifficultyChipEvent(chip.value, event)}
              >
                {chip.text}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <ul class="question-list" aria-label={`${activeTab.label} questions`} aria-live="polite">
        {#if $filteredQuestionsStore.length > 0}
          {#each $filteredQuestionsStore as question (question.id)}
            <li class="question-item">
              <h3 class="question-title">{question.prompt}</h3>
              <div class="question-meta">
                <span class="chip meta" aria-label={`Bloom tier ${question.bloom}`}>
                  {question.bloom}
                </span>
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
    </div>
  {/if}
</div>

<style>
  .question-panel {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .tablist {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tab {
    border: 1px solid var(--border-muted, #ccc);
    border-radius: 9999px;
    background: var(--surface-muted, #f7f7f7);
    color: inherit;
    padding: 0.5rem 1rem;
    cursor: pointer;
  }

  .tab.active {
    background: var(--surface-active, #005bbc);
    border-color: var(--surface-active, #005bbc);
    color: var(--text-on-primary, #fff);
  }

  .tab:focus-visible {
    outline: 3px solid var(--focus-ring, #1a73e8);
    outline-offset: 2px;
  }

  .tabpanel {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .tab-description {
    margin: 0;
    color: var(--text-subtle, #444);
  }

  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .filter-label {
    font-weight: 600;
  }

  .chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chip {
    border: 1px solid var(--border-muted, #ccc);
    border-radius: 9999px;
    background: var(--surface-muted, #f7f7f7);
    color: inherit;
    padding: 0.25rem 0.75rem;
    cursor: pointer;
  }

  .chip.active {
    background: var(--surface-active, #005bbc);
    border-color: var(--surface-active, #005bbc);
    color: var(--text-on-primary, #fff);
  }

  .chip:focus-visible {
    outline: 3px solid var(--focus-ring, #1a73e8);
    outline-offset: 2px;
  }

  .question-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .question-item {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid var(--border-muted, #ddd);
    border-radius: 12px;
    background: var(--surface-card, #fff);
  }

  .question-title {
    margin: 0;
    font-size: 1.1rem;
  }

  .question-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }

  .chip.meta {
    font-size: 0.85rem;
    background: var(--surface-muted, #eef3fb);
    border-color: var(--surface-muted, #eef3fb);
  }

  .meta-label {
    font-size: 0.9rem;
    color: var(--text-subtle, #555);
  }

  .question-location {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .location-heading {
    margin: 0;
    font-size: 1rem;
  }

  .location-list {
    margin: 0;
    padding: 0;
  }

  .location-row {
    display: flex;
    gap: 0.5rem;
  }

  .location-term {
    font-weight: 600;
  }

  .location-definition {
    margin: 0;
  }

  .location-section {
    display: block;
  }

  .location-snippet {
    margin: 0;
    font-style: italic;
  }

  .question-empty {
    padding: 1rem;
    border-radius: 12px;
    border: 1px dashed var(--border-muted, #bbb);
    text-align: center;
    color: var(--text-subtle, #555);
  }
</style>
