# EBook tooling and question generation

This workspace powers the educator workflow for the EBook reader monorepo. In addition to the Svelte UI packages, it includes a local LM Studio pipeline for generating richly annotated study questions and a durable attempt scheduler for spaced review.

## Question generation pipeline

`pipeline_lmstudio.py` extracts text from PDFs, chunks the content, and prompts LM Studio for structured questions. Each question persists the following fields:

- `question`: The rendered prompt for learners.
- `answer`: A concise, model-provided response.
- `explanation`: Supporting rationale for the answer.
- `source_span`: Verbatim evidence with `text`, `start`, and `end` offsets.

Questions are saved to both JSON (`pdf_questions.json`) and CSV (`pdf_questions.csv`) with these enriched fields, alongside chunk metadata such as summaries, keywords, and named entities.

## Attempt tracking and scheduling

The `attempt_tracking.AttemptTracker` persists learner outcomes to `attempt_log.json` and computes revisit schedules for incorrect answers. Each failed attempt backs off using a configurable exponential interval (default 15 minutes, 30 minutes, 60 minutes, ...), and queued items are exported through `review_queue.json` for the next study session.

### Usage example

```python
from attempt_tracking import AttemptTracker

tracker = AttemptTracker()
tracker.record_attempt("chunk-1-q1", correct=False)
ready_for_review = tracker.get_items_for_export()
```

Run the Python test suite to verify the scheduler logic:

```sh
python -m pytest
```

## Developing

Install dependencies and start the development server:

```sh
npm install
npm run dev
```

Everything inside `src/lib` is part of the library, and `src/routes` can be used as a showcase or preview app.

## Building

To build the library:

```sh
npm pack
```

To create a production version of the showcase app:

```sh
npm run build
```

Preview the production build with:

```sh
npm run preview
```

> To deploy the app, you may need to install an adapter for your target environment.

## Publishing

Update the `name` field in `package.json`, add licensing information, and publish to npm:

```sh
npm publish
```

## NewQuestionPanel

The `NewQuestionPanel` component renders AI-generated questions as accessible cards with interactive hint and answer reveals. Provide an array of questions where each entry includes an `id`, `stem`, `hint`, `answer`, and `whyThisMatters` message:

```svelte
<script lang="ts">
  import NewQuestionPanel from '$lib/questions/NewQuestionPanel.svelte';

  const questions = [
    {
      id: 'question-1',
      stem: 'Why did the council choose rationing?',
      hint: 'Consider the pressures on merchants and officials.',
      answer: 'Rationing balanced equity and stability.',
      whyThisMatters: 'Shows how policy makers reconcile fairness with economics.'
    }
  ];
</script>

<NewQuestionPanel {questions} />
```
