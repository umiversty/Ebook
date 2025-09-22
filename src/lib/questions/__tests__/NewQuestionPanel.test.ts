// src/lib/questions/__tests__/NewQuestionPanel.test.ts
import '@testing-library/jest-dom/vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { vi } from 'vitest';
import NewQuestionPanel from '../NewQuestionPanel.svelte';

const sampleQuestion = {
  id: 'q1',
  stem: 'Why did the council choose rationing as the primary policy response?',
  hint: 'Consider the competing priorities voiced by merchants and officials.',
  answer: 'Because supplies were scarce.',
  location: {
    section: 'Chapter 3',
    page: 42,
    offsets: [10, 50],
    snippet: 'The council debated rationing after failed harvests…'
  }
};

function renderPanel(expanded = false, toggleHint = vi.fn()) {
  return render(NewQuestionPanel, {
    props: { q: sampleQuestion, expanded, toggleHint }
  });
}

describe('NewQuestionPanel', () => {
  it('toggles the hint accordion on click and syncs aria attributes', async () => {
    const user = userEvent.setup();
    const toggleHint = vi.fn();
    renderPanel(false, toggleHint);

    const hintToggle = screen.getByRole('button', { name: /show hint/i });
    expect(hintToggle.getAttribute('aria-expanded')).toBe('false');

    await user.click(hintToggle);

    expect(toggleHint).toHaveBeenCalledTimes(1);
  });

  it('supports keyboard activation for accordion and disclosure controls', async () => {
    const toggleHint = vi.fn();
    renderPanel(false, toggleHint);

    const hintToggle = screen.getByRole('button', { name: /show hint/i });
    hintToggle.focus();

    await fireEvent.keyDown(hintToggle, { key: 'Enter' });
    expect(toggleHint).toHaveBeenCalled();

    await fireEvent.keyDown(hintToggle, { key: ' ' });
    expect(toggleHint).toHaveBeenCalledTimes(2);
  });

  it('renders source location metadata for each question', () => {
    renderPanel();

    // Section heading
    expect(screen.getByText(/chapter 3/i)).toBeInTheDocument();

    // Page indicator
    expect(screen.getByText(/page/i)).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();

    // Snippet
    expect(screen.getByText(/failed harvests/i)).toBeInTheDocument();
  });
});
