export interface EpubHeading {
  id: string;
  text: string;
  level: number;
}

export interface EpubPage {
  id: string;
  label: string;
  html: string;
  headings: EpubHeading[];
}

export interface EpubLandmark {
  id: string;
  title: string;
  href: string;
  type: 'toc' | 'body' | 'frontmatter' | 'rearnotes';
}

export interface EpubTocItem {
  id: string;
  title: string;
  href: string;
  level: number;
  headingId?: string;
  children?: EpubTocItem[];
}

export interface EvidenceCapturePayload {
  text: string;
  start: number;
  end: number;
  pageId: string;
}

export interface SearchResult {
  pageId: string;
  headingId?: string;
  snippet: string;
}
