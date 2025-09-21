import { describe, expect, it } from 'vitest';
import { applyKeyboardResize, clampColumnPx, enforceMinimumFraction, MIN_COLUMN_PX } from './splitLayout';

describe('split layout helpers', () => {
  it('applies keyboard resize respecting bounds', () => {
    const containerWidth = 960;
    const startFraction = 0.6;
    const result = applyKeyboardResize(startFraction, containerWidth, 48);
    expect(result).toBeGreaterThan(startFraction);
    const maxFraction = (containerWidth - MIN_COLUMN_PX) / containerWidth;
    expect(result).toBeLessThanOrEqual(maxFraction);
  });

  it('enforces minimum width when shrinking columns', () => {
    const containerWidth = 960;
    const belowMinimum = MIN_COLUMN_PX / containerWidth / 2;
    const enforced = enforceMinimumFraction(belowMinimum, containerWidth);
    const minFraction = MIN_COLUMN_PX / containerWidth;
    expect(enforced).toBeGreaterThanOrEqual(minFraction);
  });

  it('clamps column pixel width to minimum', () => {
    const containerWidth = 700;
    const clamped = clampColumnPx(10, containerWidth);
    expect(clamped).toBeGreaterThanOrEqual(MIN_COLUMN_PX);
  });
});
