const MATHML_NS = 'http://www.w3.org/1998/Math/MathML';
const TEX_ENCODING = 'application/x-tex';
const TEXT_ENCODING = 'text/plain';
const FALLBACK_LABEL = 'Mathematical expression';

function normaliseWhitespace(value: string | null | undefined): string {
  if (!value) return '';
  return value.replace(/\s+/g, ' ').trim();
}

function latexToReadableText(latex: string): string {
  let text = latex;
  text = text.replace(/\\frac/g, 'fraction of ');
  text = text.replace(/\\times/g, ' times ');
  text = text.replace(/\\cdot/g, ' multiplied by ');
  text = text.replace(/\\pm/g, ' plus or minus ');
  text = text.replace(/\\leq/g, ' less or equal ');
  text = text.replace(/\\geq/g, ' greater or equal ');
  text = text.replace(/\\sqrt\s*\{([^{}]+)\}/g, 'square root of $1');
  text = text.replace(/\^/g, ' to the power of ');
  text = text.replace(/_/g, ' sub ');
  text = text.replace(/\\([A-Za-z]+)/g, '$1');
  text = text.replace(/[{}]/g, ' ');
  return normaliseWhitespace(text);
}

function ensureAnnotation(mathEl: MathMLElement, latex: string | null, label: string): void {
  const doc = mathEl.ownerDocument;
  if (!doc) return;
  let semantics = mathEl.querySelector('semantics');
  if (!(semantics instanceof Element)) {
    semantics = doc.createElementNS(MATHML_NS, 'semantics');
    mathEl.appendChild(semantics);
  }

  if (latex) {
    let texAnnotation = semantics.querySelector(`annotation[encoding="${TEX_ENCODING}"]`);
    if (!texAnnotation) {
      texAnnotation = doc.createElementNS(MATHML_NS, 'annotation');
      texAnnotation.setAttribute('encoding', TEX_ENCODING);
      semantics.appendChild(texAnnotation);
    }
    texAnnotation.textContent = latex;
  }

  if (label) {
    let textAnnotation = semantics.querySelector(`annotation[encoding="${TEXT_ENCODING}"]`);
    if (!textAnnotation) {
      textAnnotation = doc.createElementNS(MATHML_NS, 'annotation');
      textAnnotation.setAttribute('encoding', TEXT_ENCODING);
      semantics.appendChild(textAnnotation);
    }
    textAnnotation.textContent = label;
  }
}

export function enhanceMathForScreenReaders(root: HTMLElement): void {
  const mathElements = Array.from(root.querySelectorAll<MathMLElement>('math'));
  mathElements.forEach((mathEl) => {
    const latex = mathEl.getAttribute('data-latex');
    const labelSource = latex ? latexToReadableText(latex) : normaliseWhitespace(mathEl.textContent);
    const finalLabel = labelSource || FALLBACK_LABEL;

    if (!mathEl.hasAttribute('tabindex')) {
      mathEl.setAttribute('tabindex', '0');
    }
    if (!mathEl.hasAttribute('aria-label')) {
      mathEl.setAttribute('aria-label', finalLabel);
    }
    ensureAnnotation(mathEl, latex, finalLabel);
  });
}

export { MATHML_NS };
