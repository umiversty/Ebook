export interface PdfOutlineItem {
  id: string;
  title: string;
  pageNumber: number;
  depth: number;
  textSpan?: { start: number; end: number } | null;
}
