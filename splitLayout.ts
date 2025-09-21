export const MIN_COLUMN_PX = 320;

export function clampColumnPx(px: number, containerWidth: number): number {
  if (containerWidth <= MIN_COLUMN_PX * 2) {
    return Math.max(MIN_COLUMN_PX, containerWidth / 2);
  }
  const max = containerWidth - MIN_COLUMN_PX;
  return Math.min(Math.max(px, MIN_COLUMN_PX), max);
}

export function fractionToPx(fraction: number, containerWidth: number): number {
  return containerWidth * fraction;
}

export function pxToFraction(px: number, containerWidth: number): number {
  if (containerWidth === 0) return 0.5;
  return px / containerWidth;
}

export function applyKeyboardResize(
  currentFraction: number,
  containerWidth: number,
  deltaPx: number
): number {
  const currentPx = fractionToPx(currentFraction, containerWidth);
  const nextPx = clampColumnPx(currentPx + deltaPx, containerWidth);
  return pxToFraction(nextPx, containerWidth);
}

export function enforceMinimumFraction(fraction: number, containerWidth: number): number {
  const px = clampColumnPx(fractionToPx(fraction, containerWidth), containerWidth);
  return pxToFraction(px, containerWidth);
}
