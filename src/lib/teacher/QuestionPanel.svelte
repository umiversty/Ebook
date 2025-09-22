<script lang="ts">
  export type QuestionChip = { text: string; ariaLabel: string; value: string };

  export let title = 'Question Library';
  export let description = 'Filter generated questions by Bloom tier or difficulty.';
  export let chips: QuestionChip[] = [];
  export let onBloomChipClick: (value: string, target: HTMLElement | null) => void = () => {};

  function handleChipClick(event: Event, value: string) {
    const target = event.currentTarget;
    onBloomChipClick(value, target instanceof HTMLElement ? target : null);
  }
</script>

<section class="question-panel" aria-label={title}>
  <header class="panel-header">
    <h2 class="panel-title">{title}</h2>
    <p class="panel-description">{description}</p>
  </header>

  <div class="chip-grid" role="group" aria-label="Question filters">
    {#if chips.length === 0}
      <p class="chip-empty">No filters configured.</p>
    {:else}
      {#each chips as chip (chip.value)}
        <button
          type="button"
          class="chip"
          aria-label={chip.ariaLabel}
          on:click={(event) => handleChipClick(event, chip.value)}
        >
          {chip.text}
        </button>
      {/each}
    {/if}
  </div>
</section>

<style>
  .question-panel {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    background: rgba(12, 18, 36, 0.85);
    border-radius: 16px;
    padding: 1.5rem;
    color: #e6e9ef;
  }

  .panel-header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .panel-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .panel-description {
    margin: 0;
    color: rgba(230, 233, 239, 0.7);
    font-size: 0.95rem;
  }

  .chip-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chip {
    border: none;
    border-radius: 999px;
    padding: 0.5rem 1rem;
    background: rgba(124, 156, 255, 0.18);
    color: inherit;
    font-weight: 500;
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

  .chip-empty {
    margin: 0;
    color: rgba(230, 233, 239, 0.6);
  }
</style>
