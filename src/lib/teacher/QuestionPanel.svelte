<script lang="ts">
  export let chips: { text: string; ariaLabel: string; value: string }[] = [];
  export let onBloomChipClick: (value: string, target: HTMLElement) => void = () => {};

  function handleChipClick(event: Event, value: string) {
    const target = event.currentTarget as HTMLButtonElement;
    onBloomChipClick(value, target);
  }
</script>

<div class="chip-panel">
  {#each chips as chip}
    <button
      aria-label={chip.ariaLabel}
      on:click={(e) => handleChipClick(e, chip.value)}
    >
      {chip.text}
    </button>
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
