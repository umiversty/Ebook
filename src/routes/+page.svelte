<script lang="ts">
  import EpubReader from '$lib/epub/EpubReader.svelte'
  import ProofofReading from '$lib/epub/proofofreading.svelte'
  import QuestionPanel from '$lib/teacher/QuestionPanel.svelte'

  // Import sample mock data
  import { sampleQuestions } from '$lib/questions/sampleQuestions'
  

  let panelOpen = true
  let menuOpen = false
</script>

<main>
  <h1>Ebook Demo</h1>

  <section class="layout">
    <!-- EPUB Reader -->
    <EpubReader
      
    />

    <!-- Proof-of-Reading -->
    <ProofofReading
      {panelOpen}
      {menuOpen}
    />

    <!-- Questions -->
    <QuestionPanel questions={sampleQuestions} />
  </section>
</main>

<style>
  main {
    padding: 1rem;
    font-family: system-ui, sans-serif;
  }

  .layout {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
    align-items: flex-start;
  }

  h1 {
    width: 100%;
    margin-bottom: 1rem;
  }
</style>
