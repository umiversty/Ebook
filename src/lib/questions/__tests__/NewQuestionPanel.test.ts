import { render, screen, within } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { tick } from 'svelte';
import { describe, expect, it } from 'vitest';
import NewQuestionPanel from '../NewQuestionPanel.svelte';
import type { GeneratedQuestion } from '../NewQuestionPanel.svelte';

const sampleQuestions: GeneratedQuestion[] = [
  {
    id: 'question-1',
    stem: 'Why did the council choose rationing as the primary policy response?',
    hint: 'Consider the competing priorities voiced by merchants and officials.',
    answer: 'Rationing balanced equitable distribution with market stability amid scarcity.',
    whyThisMatters: 'Shows how policy makers reconcile fairness with economic pressures.'
  },
  {
    id: 'question-2',
    stem: 'What evidence challenged the rumors of favoritism?',
    hint: 'Look at the audits that followed implementation.',
    answer: 'Audits contradicted favoritism claims and urged clearer public messaging.',
    whyThisMatters: 'Highlights the importance of transparency and documentation in public policy.'
  }
];

describe('NewQuestionPanel', () => {
  it('toggles the hint accordion on click and syncs aria attributes', async () => {
    const user = userEvent.setup();
    render(NewQuestionPanel, { props: { questions: sampleQuestions } });

    const questionCards = screen.getAllByRole('article');
    const firstCard = questionCards[0];

    const hintToggle = within(firstCard).getByRole('button', { name: /show hint/i });
    expect(hintToggle).toHaveAttribute('aria-expanded', 'false');

    const hintControlsId = hintToggle.getAttribute('aria-controls');
    expect(hintControlsId).toBeTruthy();
    expect(document.getElementById(hintControlsId ?? '')).toBeNull();

    await user.click(hintToggle);
    await tick();

    const hintHideToggle = within(firstCard).getByRole('button', { name: /hide hint/i });
    expect(hintHideToggle).toHaveAttribute('aria-expanded', 'true');

    const hintRegion = document.getElementById(hintControlsId ?? '');
    expect(hintRegion).toBeInTheDocument();
    expect(hintRegion).toHaveTextContent(sampleQuestions[0].hint ?? '');

    await user.click(hintHideToggle);
    await tick();

    const hintShowToggle = within(firstCard).getByRole('button', { name: /show hint/i });
    expect(hintShowToggle).toHaveAttribute('aria-expanded', 'false');
    expect(document.getElementById(hintControlsId ?? '')).toBeNull();
  });

  it('supports keyboard activation for accordion and disclosure controls', async () => {
    const user = userEvent.setup();
    render(NewQuestionPanel, { props: { questions: sampleQuestions } });

    const questionCards = screen.getAllByRole('article');
    const firstCard = questionCards[0];

    const hintToggle = within(firstCard).getByRole('button', { name: /show hint/i });
    hintToggle.focus();

    await user.keyboard('{Enter}');
    await tick();
    expect(within(firstCard).getByRole('button', { name: /hide hint/i })).toHaveAttribute(
      'aria-expanded',
      'true'
    );

    await user.keyboard('[Space]');
    await tick();
    expect(within(firstCard).getByRole('button', { name: /show hint/i })).toHaveAttribute(
      'aria-expanded',
      'false'
    );

    const answerToggle = within(firstCard).getByRole('button', { name: /show answer/i });
    answerToggle.focus();

    await user.keyboard('{Enter}');
    await tick();
    expect(within(firstCard).getByRole('button', { name: /hide answer/i })).toHaveAttribute(
      'aria-expanded',
      'true'
    );

    await user.keyboard('[Space]');
    await tick();
    expect(within(firstCard).getByRole('button', { name: /show answer/i })).toHaveAttribute(
      'aria-expanded',
      'false'
    );
  });
});
