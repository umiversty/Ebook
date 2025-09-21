import { derived, writable, type Readable, type Writable } from 'svelte/store';

import type { ReadingSection, ReadingTextSpan } from '../reading/types';

export type BloomTier = 'Remember' | 'Understand' | 'Apply' | 'Analyze';
export type Difficulty = 'Easy' | 'Medium' | 'Hard';
export type Question = {
  id: string;
  prompt: string;
  bloom: BloomTier;
  difficulty: Difficulty;
  focus: string;
  responseGuide?: string;
  readingSection: ReadingSection;
  textSpan: ReadingTextSpan;
};

export type QuestionTab = {
  id: string;
  label: string;
  description: string;
  questions: Question[];
};

export type BloomFilterValue = 'all' | BloomTier;
export type DifficultyFilterValue = 'all' | Difficulty;

export const sampleReadingSections: Record<string, ReadingSection> = {
  background: {
    id: 'section-background',
    title: 'Background',
    chapterTitle: 'Colonial Rationing Case Study',
    pageLabel: '1'
  },
  implementation: {
    id: 'section-implementation',
    title: 'Implementation',
    chapterTitle: 'Implementation',
    pageLabel: '2'
  },
  audits: {
    id: 'section-audits',
    title: 'Audits and Oversight',
    chapterTitle: 'Implementation',
    pageLabel: '2'
  },
  reflections: {
    id: 'section-reflections',
    title: 'Reflections',
    chapterTitle: 'Reflections',
    pageLabel: '3'
  },
  lessons: {
    id: 'section-lessons',
    title: 'Lessons for Modern Policy',
    chapterTitle: 'Reflections',
    pageLabel: '3'
  }
};

const rationingSpan: ReadingTextSpan = {
  startOffset: 42,
  endOffset: 214,
  text:
    'The colony faced dwindling grain reserves after a failed harvest, prompting councils to debate rationing policy for equitable distribution.'
};

const couponSpan: ReadingTextSpan = {
  startOffset: 12,
  endOffset: 168,
  text:
    'Bakers received flour allocations tied to reported demand, and coupons were issued in strict weekly increments to protect rural households.'
};

const auditSpan: ReadingTextSpan = {
  startOffset: 64,
  endOffset: 212,
  text:
    'Audits contradicted favoritism claims, documenting rotating inspection teams and recommending clearer public communication regarding ration slips.'
};

const diarySpan: ReadingTextSpan = {
  startOffset: 18,
  endOffset: 176,
  text:
    'Diaries reveal mixed reactions—relief that grain would last the winter alongside resentment of travel delays and inconsistent merchant records.'
};

const trustSpan: ReadingTextSpan = {
  startOffset: 90,
  endOffset: 198,
  text:
    'The language of official notices emphasized civic duty and mutual sacrifice, hinting that greater transparency could have eased public anxiety.'
};

export const questionTabs: QuestionTab[] = [
  {
    id: 'mcq',
    label: 'Multiple choice',
    description: 'Auto-graded comprehension checks sourced from the AI question set.',
    questions: [
      {
        id: 'mcq-1',
        prompt: 'Why did the colonial council adopt rationing measures for flour and salt?',
        bloom: 'Understand',
        difficulty: 'Easy',
        focus: 'Cause and effect reasoning',
        readingSection: sampleReadingSections.background,
        textSpan: rationingSpan
      },
      {
        id: 'mcq-2',
        prompt: 'Which evidence best shows how rationing rules tried to protect rural families?',
        bloom: 'Analyze',
        difficulty: 'Hard',
        focus: 'Evidence evaluation',
        readingSection: sampleReadingSections.implementation,
        textSpan: couponSpan
      },
      {
        id: 'mcq-3',
        prompt: 'What immediate outcome followed the council decree on ration coupons?',
        bloom: 'Remember',
        difficulty: 'Medium',
        focus: 'Key detail recall',
        readingSection: sampleReadingSections.implementation,
        textSpan: couponSpan
      }
    ]
  },
  {
    id: 'short',
    label: 'Short answer',
    description: 'Free-response prompts for discussion or exit tickets.',
    questions: [
      {
        id: 'short-1',
        prompt: 'Explain how ration inspectors balanced fairness with the limited supply of grain.',
        bloom: 'Analyze',
        difficulty: 'Medium',
        focus: 'Fairness analysis',
        responseGuide: 'Reference the audit logs and rotating inspection teams.',
        readingSection: sampleReadingSections.audits,
        textSpan: auditSpan
      },
      {
        id: 'short-2',
        prompt: 'Summarize the two biggest challenges colonists reported under the rationing policy.',
        bloom: 'Understand',
        difficulty: 'Easy',
        focus: 'Summarizing evidence',
        responseGuide: 'Highlight travel delays and inconsistent merchant records.',
        readingSection: sampleReadingSections.background,
        textSpan: diarySpan
      },
      {
        id: 'short-3',
        prompt: 'How might the council have improved trust in the rationing process?',
        bloom: 'Apply',
        difficulty: 'Hard',
        focus: 'Policy application',
        responseGuide: 'Suggest transparency steps or community audits.',
        readingSection: sampleReadingSections.reflections,
        textSpan: trustSpan
      }
    ]
  },
  {
    id: 'evidence',
    label: 'Evidence tasks',
    description: 'Prompt students to cite text snippets that justify their claims.',
    questions: [
      {
        id: 'evidence-1',
        prompt: 'Identify one passage that shows how ration coupons were distributed.',
        bloom: 'Remember',
        difficulty: 'Easy',
        focus: 'Textual evidence selection',
        readingSection: sampleReadingSections.implementation,
        textSpan: couponSpan
      },
      {
        id: 'evidence-2',
        prompt: 'Select two quotes that reveal tensions between merchants and inspectors.',
        bloom: 'Analyze',
        difficulty: 'Medium',
        focus: 'Perspective comparison',
        readingSection: sampleReadingSections.audits,
        textSpan: auditSpan
      },
      {
        id: 'evidence-3',
        prompt: 'Find evidence that supports the claim that audits reduced favoritism.',
        bloom: 'Apply',
        difficulty: 'Hard',
        focus: 'Claim support with evidence',
        readingSection: sampleReadingSections.audits,
        textSpan: auditSpan
      }
    ]
  }
];

export const tabOrder = questionTabs.map((tab) => tab.id);

export type QuestionPanelStores = {
  selectedTabId: Writable<string>;
  focusedTabId: Writable<string>;
  bloomFilter: Writable<BloomFilterValue>;
  difficultyFilter: Writable<DifficultyFilterValue>;
  filteredQuestions: Readable<Question[]>;
};

export function createQuestionPanelStores(): QuestionPanelStores {
  const selectedTabId = writable<string>(questionTabs[0].id);
  const focusedTabId = writable<string>(questionTabs[0].id);
  const bloomFilter = writable<BloomFilterValue>('all');
  const difficultyFilter = writable<DifficultyFilterValue>('all');

  const filteredQuestions = derived(
    [selectedTabId, bloomFilter, difficultyFilter],
    ([$selectedTabId, $bloomFilter, $difficultyFilter]) => {
      const activeTab = questionTabs.find((tab) => tab.id === $selectedTabId) ?? questionTabs[0];
      return activeTab.questions.filter((question) => {
        const bloomMatches = $bloomFilter === 'all' || question.bloom === $bloomFilter;
        const difficultyMatches = $difficultyFilter === 'all' || question.difficulty === $difficultyFilter;
        return bloomMatches && difficultyMatches;
      });
    }
  );

  return { selectedTabId, focusedTabId, bloomFilter, difficultyFilter, filteredQuestions };
}

export type TabNavigationContext = {
  tabOrder: string[];
  focus: (id: string) => void;
  select: (id: string) => void;
};

export function handleTabKey(
  key: string,
  currentId: string,
  context: TabNavigationContext
): boolean {
  const currentIndex = context.tabOrder.indexOf(currentId);
  if (currentIndex === -1) return false;

  if (key === 'ArrowRight' || key === 'ArrowLeft') {
    const direction = key === 'ArrowRight' ? 1 : -1;
    const nextIndex = (currentIndex + direction + context.tabOrder.length) % context.tabOrder.length;
    context.focus(context.tabOrder[nextIndex]);
    return true;
  }

  if (key === 'Home') {
    context.focus(context.tabOrder[0]);
    return true;
  }

  if (key === 'End') {
    context.focus(context.tabOrder[context.tabOrder.length - 1]);
    return true;
  }

  if (key === 'Enter' || key === ' ') {
    context.select(currentId);
    return true;
  }

  return false;
}

export const bloomChips: Array<{ value: BloomFilterValue; text: string; ariaLabel: string }> = [
  { value: 'all', text: 'All tiers', ariaLabel: 'Show all Bloom tiers' },
  { value: 'Remember', text: 'Remember', ariaLabel: 'Bloom tier: Remember' },
  { value: 'Understand', text: 'Understand', ariaLabel: 'Bloom tier: Understand' },
  { value: 'Apply', text: 'Apply', ariaLabel: 'Bloom tier: Apply' },
  { value: 'Analyze', text: 'Analyze', ariaLabel: 'Bloom tier: Analyze' }
];

export const difficultyChips: Array<{ value: DifficultyFilterValue; text: string; ariaLabel: string }> = [
  { value: 'all', text: 'All levels', ariaLabel: 'Show all difficulty levels' },
  { value: 'Easy', text: 'Easy', ariaLabel: 'Difficulty: Easy' },
  { value: 'Medium', text: 'Medium', ariaLabel: 'Difficulty: Medium' },
  { value: 'Hard', text: 'Hard', ariaLabel: 'Difficulty: Hard' }
];

export function updateBloomFilter(
  store: Writable<BloomFilterValue>,
  value: BloomFilterValue,
  target: HTMLButtonElement | null
) {
  store.set(value);
  target?.focus();
}

export function updateDifficultyFilter(
  store: Writable<DifficultyFilterValue>,
  value: DifficultyFilterValue,
  target: HTMLButtonElement | null
) {
  store.set(value);
  target?.focus();
}
