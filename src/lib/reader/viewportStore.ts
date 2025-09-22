import { writable } from 'svelte/store';

const DEFAULT_WIDTH = typeof window !== 'undefined' ? window.innerWidth : 720;

const viewportWidth = writable<number>(DEFAULT_WIDTH);

export const viewportWidthStore = viewportWidth;

export function setViewportWidth(width: number) {
  viewportWidth.set(width);
}
