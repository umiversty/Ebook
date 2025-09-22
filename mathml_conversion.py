"""MathML conversion utilities for math-heavy learning materials."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable, Iterable, Optional
import xml.etree.ElementTree as ET

MATHML_NS = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", MATHML_NS)

InlineConverter = Callable[[str], str]

INLINE_MATH_PATTERN = re.compile(r"(?<!\\)\$(?P<expr>.+?)(?<!\\)\$", re.DOTALL)
DOUBLE_DOLLAR_PATTERN = re.compile(r"(?<!\\)\$\$(?P<expr>.+?)(?<!\\)\$\$", re.DOTALL)
DISPLAY_PATTERN = re.compile(
    r"\\\[(?P<bracket>.+?)\\\]|\\begin\{(?P<env>equation\*?|align\*?)\}(?P<body>[\\s\\S]+?)\\end\{(?P=env)\}",
    re.DOTALL,
)


def _latex_to_plain_text(latex: str) -> str:
    """Generate a crude speech-friendly text alternative for ``latex``."""

    text = latex.replace("\\frac", "fraction of")
    text = text.replace("\\times", " times ")
    text = text.replace("\\cdot", " multiplied by ")
    text = text.replace("\\pm", " plus or minus ")
    text = text.replace("\\leq", " less or equal ")
    text = text.replace("\\geq", " greater or equal ")
    text = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"square root of \1", text)
    text = text.replace("^", " to the power of ")
    text = text.replace("_", " sub ")
    text = re.sub(r"\\[A-Za-z]+", lambda m: m.group(0)[1:], text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@dataclass
class LatexMathMLConverter:
    """Converts LaTeX expressions to MathML with semantic annotations."""

    convert_func: Optional[InlineConverter] = None

    def __post_init__(self) -> None:  # pragma: no cover - exercised in production
        if self.convert_func is None:
            try:
                from latex2mathml.converter import convert  # type: ignore

                self.convert_func = convert
            except Exception:  # pragma: no cover - dependency optional
                self.convert_func = None

    def convert(self, latex: str, *, display: bool = False) -> str:
        """Convert ``latex`` into MathML, falling back to readable mtext."""

        cleaned = latex.strip()
        if not cleaned:
            return ""

        mathml: str = ""
        if self.convert_func is not None:
            try:
                mathml = self.convert_func(cleaned)
            except Exception:
                mathml = ""

        if not mathml:
            return self._fallback_mathml(cleaned, display=display)

        return self._normalise_mathml(mathml, cleaned, display=display)

    # --------------------------
    # Internal helpers
    # --------------------------
    def _normalise_mathml(self, mathml: str, latex: str, *, display: bool) -> str:
        """Ensure the generated MathML is navigable and annotated."""

        try:
            root = ET.fromstring(mathml)
        except ET.ParseError:
            return self._fallback_mathml(latex, display=display)

        if not self._is_math_element(root):
            wrapper = ET.Element(f"{{{MATHML_NS}}}math")
            wrapper.set("display", "block" if display else "inline")
            wrapper.set("data-latex", latex)
            wrapper.append(root)
            root = wrapper
        else:
            root.set("display", "block" if display else "inline")
            root.set("data-latex", latex)

        semantics = root.find(f"{{{MATHML_NS}}}semantics")
        if semantics is None:
            semantics = ET.SubElement(root, f"{{{MATHML_NS}}}semantics")

        annotation_tex = None
        for child in semantics.findall(f"{{{MATHML_NS}}}annotation"):
            if child.get("encoding") == "application/x-tex":
                annotation_tex = child
                break
        if annotation_tex is None:
            annotation_tex = ET.SubElement(
                semantics, f"{{{MATHML_NS}}}annotation", encoding="application/x-tex"
            )
        annotation_tex.text = latex

        text_annotation = None
        for child in semantics.findall(f"{{{MATHML_NS}}}annotation"):
            if child.get("encoding") == "text/plain":
                text_annotation = child
                break
        if text_annotation is None:
            text_annotation = ET.SubElement(
                semantics, f"{{{MATHML_NS}}}annotation", encoding="text/plain"
            )
        text_annotation.text = _latex_to_plain_text(latex)

        return ET.tostring(root, encoding="unicode")

    def _fallback_mathml(self, latex: str, *, display: bool) -> str:
        """Build a semantic ``mtext`` fallback that remains selectable."""

        math = ET.Element(f"{{{MATHML_NS}}}math")
        math.set("display", "block" if display else "inline")
        math.set("data-latex", latex)
        mrow = ET.SubElement(math, f"{{{MATHML_NS}}}mrow")
        mtext = ET.SubElement(mrow, f"{{{MATHML_NS}}}mtext")
        mtext.text = latex
        semantics = ET.SubElement(math, f"{{{MATHML_NS}}}semantics")
        annotation_tex = ET.SubElement(
            semantics, f"{{{MATHML_NS}}}annotation", encoding="application/x-tex"
        )
        annotation_tex.text = latex
        annotation_text = ET.SubElement(
            semantics, f"{{{MATHML_NS}}}annotation", encoding="text/plain"
        )
        annotation_text.text = _latex_to_plain_text(latex)
        return ET.tostring(math, encoding="unicode")

    @staticmethod
    def _is_math_element(element: ET.Element) -> bool:
        return element.tag.endswith("math")


def convert_latex_segments_to_mathml(text: str, converter: LatexMathMLConverter) -> str:
    """Convert inline and display math markers inside ``text`` to MathML."""

    if not text:
        return ""

    def _replace_double(match: re.Match[str]) -> str:
        expr = match.group("expr") or ""
        return converter.convert(expr, display=True)

    converted = DOUBLE_DOLLAR_PATTERN.sub(_replace_double, text)

    def _replace_display(match: re.Match[str]) -> str:
        expr = match.group("bracket") or match.group("body") or ""
        return converter.convert(expr, display=True)

    converted = DISPLAY_PATTERN.sub(_replace_display, converted)

    def _replace_inline(match: re.Match[str]) -> str:
        expr = match.group("expr") or ""
        return converter.convert(expr, display=False)

    converted = INLINE_MATH_PATTERN.sub(_replace_inline, converted)

    return converted


def pdf_page_to_html_overlay(page: "PDFPage", converter: LatexMathMLConverter) -> str:
    """Render a :class:`PDFPage` into a MathML-friendly HTML overlay snippet."""

    paragraphs = [seg.strip() for seg in re.split(r"\n{2,}", page.text) if seg.strip()]
    if not paragraphs:
        return ""

    rendered: list[str] = [
        f'<section role="doc-page" data-page-index="{page.index}">' 
    ]
    for para in paragraphs:
        converted = convert_latex_segments_to_mathml(para, converter)
        rendered.append(f"  <p>{converted}</p>")
    rendered.append("</section>")
    return "\n".join(rendered)


def convert_pdf_pages_to_html_overlays(
    pages: Iterable["PDFPage"],
    converter: Optional[LatexMathMLConverter] = None,
) -> list[str]:
    """Convert pages to HTML overlays with MathML content."""

    converter = converter or LatexMathMLConverter()
    overlays: list[str] = []
    for page in pages:
        html = pdf_page_to_html_overlay(page, converter)
        if html:
            overlays.append(html)
    return overlays
