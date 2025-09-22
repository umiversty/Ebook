export interface ReadingSection {
  id: string;
  title: string;
  chapterTitle: string;
  pageLabel: string;
}

export interface ReadingTextSpan {
  startOffset: number;
  endOffset: number;
  text: string;
}

export interface ReadingLocation {
  section: ReadingSection;
  span: ReadingTextSpan;
}
