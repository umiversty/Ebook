import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';

import QuestionPanel from '../QuestionPanel.svelte';
import {
  createQuestionPanelStores,
  updateBloomFilter,
  updateDifficultyFilter
} from '../questionPanelState';

describe('QuestionPanel component', () => {
  it('filters questions by Bloom tier and updates accessibility state', async () => {
    render(QuestionPanel);

    const analyzeChip = screen.getByRole('button', { name: /Bloom tier: Analyze/i });
    await fireEvent.click(analyzeChip);

    expect(analyzeChip).toHaveAttribute('aria-pressed', 'true');
    const questionHeadings = screen.getAllByRole('heading', { level: 3 });
    expect(questionHeadings).toHaveLength(1);
    expect(questionHeadings[0]).toHaveTextContent(/Which evidence best shows/i);
  });

  it('invokes provided chip callbacks with the selected value and element', async () => {
    const stores = createQuestionPanelStores();
    const bloomSpy = vi.fn((value, target: HTMLButtonElement | null) => {
      updateBloomFilter(stores.bloomFilter, value, target);
    });
    const difficultySpy = vi.fn((value, target: HTMLButtonElement | null) => {
      updateDifficultyFilter(stores.difficultyFilter, value, target);
    });

    render(QuestionPanel, {
      props: {
        stores,
        onBloomChipClick: bloomSpy,
        onDifficultyChipClick: difficultySpy
      }
    });

    const rememberChip = screen.getByRole('button', { name: /Bloom tier: Remember/i });
    await fireEvent.click(rememberChip);

    expect(bloomSpy).toHaveBeenCalledTimes(1);
    expect(bloomSpy).toHaveBeenCalledWith('Remember', rememberChip);
    expect(rememberChip).toHaveAttribute('aria-pressed', 'true');

    const hardChip = screen.getByRole('button', { name: /Difficulty: Hard/i });
    await fireEvent.click(hardChip);

    expect(difficultySpy).toHaveBeenCalledTimes(1);
    expect(difficultySpy).toHaveBeenCalledWith('Hard', hardChip);
    expect(hardChip).toHaveAttribute('aria-pressed', 'true');

    expect(screen.getByText(/No questions match the selected filters/i)).toBeInTheDocument();
  });
});
