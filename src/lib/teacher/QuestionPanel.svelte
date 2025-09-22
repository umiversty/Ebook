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
    type QuestionPanelStores,
    type QuestionTab
  } from './questionPanelState';

  export let stores: QuestionPanelStores | undefined = undefined;
  export let onBloomChipClick:
    | ((value: BloomFilterValue, target: HTMLButtonElement | null) => void)
    | undefined = undefined;
  export let onDifficultyChipClick:
    | ((value: DifficultyFilterValue, target: HTMLButtonElement | null) => void)
    | undefined = undefined;

  const fallbackStores = createQuestionPanelStores();
  let resolvedStores: QuestionPanelStores = stores ?? fallbackStores;

  $: if (stores) {
    resolvedStores = stores;
  }

  const tabRefs = new Map<string, HTMLButtonElement>();

  const { selectedTabId, focusedTabId, bloomFilter, difficultyFilter, filteredQuestions } =
    resolvedStores;

  let activeTab: QuestionTab = questionTabs[0];
  $: activeTab = questionTabs.find((tab) => tab.id === $selectedTabId) ?? questionTabs[0];

  function registerTab(id: string, element: HTMLButtonElement | null) {
    if (element) {
      tabRefs.set(id, element);
    } else {
      tabRefs.delete(id);
    }
  }

  function tabRegistrationAction(node: HTMLButtonElement, id: string) {
    let currentId = id;
    registerTab(currentId, node);

    return {
      update(newId: string) {
        if (newId !== currentId) {
          registerTab(currentId, null);
          currentId = newId;
          registerTab(currentId, node);
        }
      },
      destroy() {
        registerTab(currentId, null);
      }
    };
  }

  function focusTab(id: string) {
    focusedTabId.set(id);
    const element = tabRefs.get(id);
    element?.focus();
  }

  function selectTab(id: string) {
    selectedTabId.set(id);
    focusTab(id);
  }

  function onTabKeydown(event: KeyboardEvent, id: string) {
    const handled = handleTabKey(event.key, id, {
      tabOrder,
      focus: focusTab,
      select: selectTab
    });

    if (handled) {
      event.preventDefault();
    }
  }

  function handleBloomClick(value: BloomFilterValue, event: MouseEvent) {
    const target = event.currentTarget as HTMLButtonElement | null;
    if (onBloomChipClick) {
      onBloomChipClick(value, target);
    } else {
      updateBloomFilter(bloomFilter, value, target);
    }
  }

  function handleDifficultyClick(value: DifficultyFilterValue, event: MouseEvent) {
    const target = event.currentTarget as HTMLButtonElement | null;
    if (onDifficultyChipClick) {
      onDifficultyChipClick(value, target);
    } else {
      updateDifficultyFilter(difficultyFilter, value, target);
    }
  }
</script>

<div class="question-panel">
  <div class="tabs" role="tablist" aria-label="Question types">
    {#each questionTabs as tab}
      <button
        id={`tab-${tab.id}`}
        class="tab"
        class:active={tab.id === $selectedTabId}
        role="tab"
        type="button"
        aria-selected={tab.id === $selectedTabId ? 'true' : 'false'}
        aria-controls={`panel-${tab.id}`}
        tabindex={tab.id === $focusedTabId ? 0 : -1}
        on:click={() => selectTab(tab.id)}
        on:keydown={(event) => onTabKeydown(event, tab.id)}
        on:focus={() => focusTab(tab.id)}
        use:tabRegistrationAction={tab.id}
      >
        {tab.label}
      </button>
    {/each}
  </div>

  <div
    id={`panel-${activeTab.id}`}
    class="tabpanel"
    role="tabpanel"
    aria-labelledby={`tab-${activeTab.id}`}
  >
    <p class="tab-description">{activeTab.description}</p>

    <div class="filters">
      <div class="filter-group" role="group" aria-labelledby="bloom-filter-label">
        <span id="bloom-filter-label" class="filter-label">Bloom tier</span>
        <div class="chip-row">
          {#each bloomChips as chip}
            <button
              type="button"
              class="chip"
              class:active={$bloomFilter === chip.value}
              aria-pressed={$bloomFilter === chip.value ? 'true' : 'false'}
              aria-label={chip.ariaLabel}
              on:click={(event) => handleBloomClick(chip.value, event)}
            >
              {chip.text}
            </button>
          {/each}
        </div>
      </div>

      <div class="filter-group" role="group" aria-labelledby="difficulty-filter-label">
        <span id="difficulty-filter-label" class="filter-label">Difficulty</span>
        <div class="chip-row">
          {#each difficultyChips as chip}
            <button
              type="button"
              class="chip"
              class:active={$difficultyFilter === chip.value}
              aria-pressed={$difficultyFilter === chip.value ? 'true' : 'false'}
              aria-label={chip.ariaLabel}
              on:click={(event) => handleDifficultyClick(chip.value, event)}
            >
              {chip.text}
            </button>
          {/each}
        </div>
      </div>
    </div>

    {#if $filteredQuestions.length > 0}
      <ul class="question-list">
        {#each $filteredQuestions as question (question.id)}
          <li class="question-item">
            <h3 class="question-title">{question.prompt}</h3>
            <div class="question-meta">
              <span class="meta-label">Bloom</span>
              <span class="chip meta">{question.bloom}</span>
              <span class="meta-label">Difficulty</span>
              <span class="chip meta">{question.difficulty}</span>
            </div>
            <p class="meta-label">Focus: {question.focus}</p>
            {#if question.responseGuide}
              <p class="response-guide">Response guide: {question.responseGuide}</p>
            {/if}
            <div class="question-location">
              <h4 class="location-heading">Where to find it</h4>
              <dl class="location-list">
                <div class="location-row">
                  <dt class="location-term">Section</dt>
                  <dd class="location-definition">
                    <span class="location-section">{question.readingSection.title}</span>
                  </dd>
                </div>
                <div class="location-row">
                  <dt class="location-term">Chapter</dt>
                  <dd class="location-definition">{question.readingSection.chapterTitle}</dd>
                </div>
                <div class="location-row">
                  <dt class="location-term">Page</dt>
                  <dd class="location-definition">{question.readingSection.pageLabel}</dd>
                </div>
              </dl>
              <p class="location-snippet">{question.textSpan.text}</p>
            </div>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="question-empty">No questions match the selected filters.</p>
    {/if}
  </div>
</div>

<style>
  .question-panel {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .tab {
    border: 1px solid var(--border-muted, #c5cbe0);
    border-radius: 9999px;
    background: var(--surface-muted, #eef3fb);
    color: inherit;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: background 0.2s ease, transform 0.2s ease;
  }

  .tab:hover,
  .tab:focus-visible {
    background: rgba(124, 156, 255, 0.35);
    outline: none;
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
    transition: background 0.2s ease, transform 0.2s ease;
  }

  .chip:hover,
  .chip:focus-visible {
    background: rgba(124, 156, 255, 0.35);
    outline: none;
  }

  .chip:focus-visible {
    box-shadow: 0 0 0 3px rgba(124, 156, 255, 0.5);
  }

  .chip.active {
    background: var(--surface-active, #005bbc);
    border-color: var(--surface-active, #005bbc);
    color: var(--text-on-primary, #fff);
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
