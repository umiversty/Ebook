import { describe, expect, it } from 'vitest';
import { get } from 'svelte/store';

import {
  createQuestionPanelStores,
  handleTabKey,
  questionTabs,
  tabOrder,
  updateBloomFilter,
  updateDifficultyFilter
} from '../questionPanelState';

describe('question panel state', () => {
  it('computes roving tabindex focus without mutating selection', () => {
    const focusCalls: string[] = [];
    const selectCalls: string[] = [];
    const context = {
      tabOrder,
      focus: (id: string) => focusCalls.push(id),
      select: (id: string) => selectCalls.push(id)
    };

    const firstId = tabOrder[0];
    const secondId = tabOrder[1];
    const lastId = tabOrder[tabOrder.length - 1];

    expect(handleTabKey('ArrowRight', firstId, context)).toBe(true);
    expect(focusCalls).toEqual([secondId]);
    expect(selectCalls).toEqual([]);

    focusCalls.length = 0;
    expect(handleTabKey('Home', secondId, context)).toBe(true);
    expect(focusCalls).toEqual([firstId]);
    expect(selectCalls).toEqual([]);

    focusCalls.length = 0;
    expect(handleTabKey('End', firstId, context)).toBe(true);
    expect(focusCalls).toEqual([lastId]);
    expect(selectCalls).toEqual([]);

    focusCalls.length = 0;
    expect(handleTabKey('Enter', firstId, context)).toBe(true);
    expect(selectCalls).toEqual([firstId]);
  });

  it('filters questions by Bloom tier and difficulty while preserving chip focus', () => {
    const { selectedTabId, bloomFilter, difficultyFilter, filteredQuestions } =
      createQuestionPanelStores();

    selectedTabId.set(questionTabs[0].id);
    expect(get(filteredQuestions)).toHaveLength(questionTabs[0].questions.length);

    const hardChip = document.createElement('button');
    document.body.appendChild(hardChip);
    updateDifficultyFilter(difficultyFilter, 'Hard', hardChip);
    expect(document.activeElement).toBe(hardChip);
    expect(get(filteredQuestions).map((q) => q.id)).toEqual(['mcq-2']);

    const analyzeChip = document.createElement('button');
    document.body.appendChild(analyzeChip);
    updateBloomFilter(bloomFilter, 'Analyze', analyzeChip);
    expect(document.activeElement).toBe(analyzeChip);
    expect(get(filteredQuestions).map((q) => q.id)).toEqual(['mcq-2']);

    const allDifficultyChip = document.createElement('button');
    document.body.appendChild(allDifficultyChip);
    updateDifficultyFilter(difficultyFilter, 'all', allDifficultyChip);
    expect(document.activeElement).toBe(allDifficultyChip);
    expect(get(filteredQuestions).map((q) => q.id)).toEqual(['mcq-2']);

    const allBloomChip = document.createElement('button');
    document.body.appendChild(allBloomChip);
    updateBloomFilter(bloomFilter, 'all', allBloomChip);
    expect(document.activeElement).toBe(allBloomChip);
    expect(get(filteredQuestions).length).toBeGreaterThan(1);

    hardChip.remove();
    analyzeChip.remove();
    allDifficultyChip.remove();
    allBloomChip.remove();
  });
});
