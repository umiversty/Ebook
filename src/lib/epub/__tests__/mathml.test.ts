import { describe, expect, it } from 'vitest';
import { MATHML_NS, enhanceMathForScreenReaders } from '../mathml.js';

describe('enhanceMathForScreenReaders', () => {
  it('makes math elements focusable and labelled', () => {
    const container = document.createElement('div');
    container.innerHTML = `<math xmlns="${MATHML_NS}" data-latex="E=mc^2"><mrow><mi>E</mi></mrow></math>`;

    enhanceMathForScreenReaders(container);

    const mathEl = container.querySelector('math');
    expect(mathEl).not.toBeNull();
    expect(mathEl?.getAttribute('tabindex')).toBe('0');
    expect(mathEl?.getAttribute('aria-label')).toContain('E');
    const annotation = mathEl?.querySelector(`annotation[encoding="application/x-tex"]`);
    expect(annotation?.textContent).toBe('E=mc^2');
  });

  it('adds fallback labels when no latex data is present', () => {
    const container = document.createElement('div');
    container.innerHTML = `<math xmlns="${MATHML_NS}"><mrow><mi>x</mi></mrow></math>`;

    enhanceMathForScreenReaders(container);

    const mathEl = container.querySelector('math');
    expect(mathEl?.getAttribute('aria-label')).toBeTruthy();
  });
});
