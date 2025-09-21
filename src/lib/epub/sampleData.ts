import type { EpubLandmark, EpubPage, EpubTocItem } from './types.js';

export const samplePages: EpubPage[] = [
  {
    id: 'page-1',
    label: '1',
    html: `
<section role="doc-chapter" aria-labelledby="chapter-rationing">
  <h1 id="chapter-rationing" data-epub-heading data-level="1" role="doc-title">Colonial Rationing Case Study</h1>
  <p>The colony faced dwindling grain reserves after a failed harvest. Councils debated rationing policy and merchants argued for price ceilings while officials pushed for equitable distribution.</p>
  <h2 id="chapter-rationing-background" data-epub-heading data-level="2" role="doc-heading">Background</h2>
  <p>Diaries from the period reveal mixed reactions among townspeople, noting both relief and resentment. Implementation of ration books began the following month.</p>
</section>
`,
    headings: [
      { id: 'chapter-rationing', text: 'Colonial Rationing Case Study', level: 1 },
      { id: 'chapter-rationing-background', text: 'Background', level: 2 }
    ]
  },
  {
    id: 'page-2',
    label: '2',
    html: `
<section role="doc-chapter" aria-labelledby="chapter-implementation">
  <h1 id="chapter-implementation" data-epub-heading data-level="1" role="doc-heading">Implementation</h1>
  <p>Bakers received flour allocations tied to reported demand. Rumors of favoritism spread, particularly concerning officials and their associates.</p>
  <h2 id="chapter-implementation-audits" data-epub-heading data-level="2" role="doc-subtitle">Audits and Oversight</h2>
  <p>Audits later contradicted some claims and recommended clearer public communication regarding ration slips.</p>
</section>
`,
    headings: [
      { id: 'chapter-implementation', text: 'Implementation', level: 1 },
      { id: 'chapter-implementation-audits', text: 'Audits and Oversight', level: 2 }
    ]
  },
  {
    id: 'page-3',
    label: '3',
    html: `
<section role="doc-chapter" aria-labelledby="chapter-reflection">
  <h1 id="chapter-reflection" data-epub-heading data-level="1" role="doc-heading">Reflections</h1>
  <p>Historians point out that rationing systems are often perceived as unfair in the short term but can stabilize markets over time.</p>
  <h2 id="chapter-reflection-lessons" data-epub-heading data-level="2" role="doc-heading">Lessons for Modern Policy</h2>
  <p>The language of official notices emphasized civic duty and mutual sacrifice, while diaries reveal anxiety over scarcity and social standing.</p>
</section>
`,
    headings: [
      { id: 'chapter-reflection', text: 'Reflections', level: 1 },
      { id: 'chapter-reflection-lessons', text: 'Lessons for Modern Policy', level: 2 }
    ]
  }
];

export const sampleToc: EpubTocItem[] = [
  {
    id: 'toc-root',
    title: 'Colonial Rationing Case Study',
    href: '#chapter-rationing',
    level: 1,
    headingId: 'chapter-rationing',
    children: [
      {
        id: 'toc-background',
        title: 'Background',
        href: '#chapter-rationing-background',
        level: 2,
        headingId: 'chapter-rationing-background'
      },
      {
        id: 'toc-implementation',
        title: 'Implementation',
        href: '#chapter-implementation',
        level: 2,
        headingId: 'chapter-implementation'
      },
      {
        id: 'toc-reflections',
        title: 'Reflections',
        href: '#chapter-reflection',
        level: 2,
        headingId: 'chapter-reflection'
      }
    ]
  }
];

export const sampleLandmarks: EpubLandmark[] = [
  { id: 'landmark-toc', title: 'Table of contents', href: '#chapter-rationing', type: 'toc' },
  { id: 'landmark-body', title: 'Main narrative', href: '#chapter-implementation', type: 'body' },
  { id: 'landmark-ref', title: 'Historical reflection', href: '#chapter-reflection', type: 'rearnotes' }
];
