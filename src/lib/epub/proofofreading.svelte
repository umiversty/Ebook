<script lang="ts">
  export let tasks: { id: number; done: boolean; answer?: string }[] = [];
  export let setAnswer: (id: number, value: string) => void;
</script>

{#each tasks as t}
  <div class="task">
    {#if t.done}
      <div
        class="pill"
        style="margin-top:6px;background:rgba(61,220,151,.18); color: #3ddc97;"
      >
        Completed
      </div>
    {:else}
      <textarea
  class="card"
  rows="3"
  placeholder="Type your response…"
  value={t.answer || ''}
  on:input={(e) => setAnswer(t.id, e.currentTarget.value)}
/>

    {/if}
  </div>
{/each}

<style>
  .pill {
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.9rem;
  }
  .card {
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 6px;
  }
</style>
