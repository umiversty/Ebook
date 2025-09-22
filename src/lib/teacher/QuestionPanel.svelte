<script lang="ts">

  }
</script>


    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }


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
