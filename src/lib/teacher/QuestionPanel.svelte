<script lang="ts">
  import type { Action } from 'svelte/action';
  import {
    bloomChips,
    createQuestionPanelStores,
    difficultyChips,
    handleTabKey,
    questionTabs,
    tabOrder,
    updateBloomFilter,
    updateDifficultyFilter
  } from './questionPanelState';

  type BloomChipValue = (typeof bloomChips)[number]['value'];
  type DifficultyChipValue = (typeof difficultyChips)[number]['value'];

  const { selectedTabId, focusedTabId, bloomFilter, difficultyFilter, filteredQuestions } =
    createQuestionPanelStores();

  const tabRefs = new Map<string, HTMLButtonElement>();

  const registerTab: Action<HTMLButtonElement, string> = (node, id) => {
    let currentId = id;
    if (currentId) {
      tabRefs.set(currentId, node);
    }
    return {
      update(newId) {
        if (currentId === newId) return;
        if (currentId) {
          tabRefs.delete(currentId);
        }
        currentId = newId;
        if (currentId) {
          tabRefs.set(currentId, node);
        }
      },
      destroy() {
        if (currentId) {
          tabRefs.delete(currentId);
        }
      }
    };
  };

  function focusTab(id: string) {
    focusedTabId.set(id);
    tabRefs.get(id)?.focus();
  }

  function selectTab(id: string) {
    selectedTabId.set(id);
    focusTab(id);
  }

  function onTabKeydown(event: KeyboardEvent, currentId: string) {
    const handled = handleTabKey(event.key, currentId, {
      tabOrder,
      focus: focusTab,
      select: selectTab
    });
    if (handled) {
      event.preventDefault();
    }
  }

  function onBloomChipClick(value: BloomChipValue, target: HTMLButtonElement | null) {
    updateBloomFilter(bloomFilter, value, target);
  }

  function onDifficultyChipClick(value: DifficultyChipValue, target: HTMLButtonElement | null) {
    updateDifficultyFilter(difficultyFilter, value, target);
  }

  function handleBloomChipEvent(value: BloomChipValue, event: Event) {
    onBloomChipClick(value, event.currentTarget as HTMLButtonElement | null);
  }

  function handleDifficultyChipEvent(value: DifficultyChipValue, event: Event) {
    onDifficultyChipClick(value, event.currentTarget as HTMLButtonElement | null);
  }
</script>

<section class="question-panel">
  <header class="panel-header">
    <div>
      <h2 class="panel-title">Question bank</h2>
      <p class="panel-subtitle">Preview AI-generated prompts before creating assignments.</p>
    </div>
  </header>

  <div class="tablist" role="tablist" aria-label="Question types">
    {#each questionTabs as tab (tab.id)}
      <button
        use:registerTab={tab.id}
        id={`question-tab-${tab.id}`}
        class="tab"
        role="tab"
        type="button"
        aria-selected={$selectedTabId === tab.id}
        aria-controls={`question-panel-${tab.id}`}
        tabindex={$focusedTabId === tab.id ? 0 : -1}
        on:click={() => selectTab(tab.id)}
        on:keydown={(event) => onTabKeydown(event, tab.id)}
      >
        <span class="tab-label">{tab.label}</span>
        <span class="tab-count" aria-hidden="true">{tab.questions.length}</span>
      </button>
    {/each}
  </div>

  {#each questionTabs as tab (tab.id)}
    <div
      id={`question-panel-${tab.id}`}
      class="tabpanel"
      role="tabpanel"
      aria-labelledby={`question-tab-${tab.id}`}
      tabindex="0"
      hidden={$selectedTabId !== tab.id}
    >
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
              </li>
            {/each}
          {:else}
            <li class="question-empty">No questions match the selected filters.</li>
          {/if}
        </ul>
      {/if}
    </div>
  {/each}
</section>

<style>
  .question-panel {
    background: #0f1428;
    border-radius: 16px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .panel-title {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e6e9ef;
  }

  .panel-subtitle {
    margin: 4px 0 0 0;
    color: #9aa3b2;
    font-size: 0.9rem;
  }

  .tablist {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .tab {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    color: #e6e9ef;
    font-weight: 600;
    padding: 8px 14px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .tab:focus {
    outline: none;
  }

  .tab:focus-visible {
    outline: 4px solid rgba(195, 212, 255, 0.9);
    outline-offset: 2px;
  }

  .tab[aria-selected='true'] {
    background: rgba(124, 156, 255, 0.2);
    border-color: rgba(124, 156, 255, 0.5);
    color: #ffffff;
  }

  .tab-count {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    font-size: 0.75rem;
    padding: 2px 8px;
  }

  .tabpanel[hidden] {
    display: none;
  }

  .tab-description {
    color: #9aa3b2;
    margin: 0;
  }

  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-label {
    color: #9aa3b2;
    font-size: 0.85rem;
  }

  .chip-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .chip {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid transparent;
    border-radius: 999px;
    color: #e6e9ef;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 6px 12px;
  }

  .chip:focus {
    outline: none;
  }

  .chip:focus-visible {
    box-shadow: 0 0 0 4px rgba(124, 156, 255, 0.6);
  }

  .chip.active {
    background: rgba(61, 220, 151, 0.2);
    border-color: rgba(61, 220, 151, 0.6);
    color: #3ddc97;
  }

  .chip.meta {
    background: rgba(255, 255, 255, 0.06);
    border: none;
    color: #e6e9ef;
    font-weight: 500;
  }

  .question-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .question-item {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 12px;
  }

  .question-title {
    margin: 0 0 8px 0;
    font-size: 1rem;
    color: #ffffff;
  }

  .question-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    color: #9aa3b2;
    font-size: 0.8rem;
  }

  .meta-label {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    padding: 4px 10px;
  }

  .question-empty {
    color: #9aa3b2;
    font-style: italic;
  }
</style>
