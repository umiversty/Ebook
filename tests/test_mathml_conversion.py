import re

import pytest

from mathml_conversion import (
    MATHML_NS,
    LatexMathMLConverter,
    convert_latex_segments_to_mathml,
)
from pipeline_lmstudio import (
    PDFPage,
    convert_document_to_mathml_overlays,
    convert_page_text_to_mathml_html,
    convert_text_block_to_mathml,
)


@pytest.fixture()
def stub_converter() -> LatexMathMLConverter:
    def _convert(latex: str) -> str:
        return (
            f'<math xmlns="{MATHML_NS}"><mrow><mi>{latex}</mi></mrow></math>'
        )

    return LatexMathMLConverter(convert_func=_convert)


def test_converter_wraps_mathml_with_annotations(stub_converter: LatexMathMLConverter) -> None:
    mathml = stub_converter.convert("E=mc^2", display=False)
    assert 'data-latex="E=mc^2"' in mathml
    assert 'display="inline"' in mathml
    assert 'annotation encoding="application/x-tex">E=mc^2' in mathml
    assert 'annotation encoding="text/plain"' in mathml


def test_converter_falls_back_to_mtext_when_library_missing() -> None:
    def _raise(_: str) -> str:
        raise RuntimeError("boom")

    converter = LatexMathMLConverter(convert_func=_raise)
    mathml = converter.convert("x+1", display=True)
    assert 'display="block"' in mathml
    assert '<mtext>x+1</mtext>' in mathml


def test_inline_and_display_segments_are_converted(stub_converter: LatexMathMLConverter) -> None:
    text = "The relation $E=mc^2$ is equivalent to $$E^2 = (mc^2)^2$$."
    converted = convert_latex_segments_to_mathml(text, stub_converter)
    assert converted.count('<math') == 2
    assert 'data-latex="E=mc^2"' in converted


def test_pdf_page_conversion_produces_section(stub_converter: LatexMathMLConverter) -> None:
    page = PDFPage(index=1, text="Energy example\n\n$E=mc^2$")
    html = convert_page_text_to_mathml_html(page, converter=stub_converter)
    assert html.startswith('<section')
    assert 'data-page-index="1"' in html
    assert html.count('<math') == 1


def test_document_conversion_filters_empty_pages(stub_converter: LatexMathMLConverter) -> None:
    pages = [
        PDFPage(index=1, text=""),
        PDFPage(index=2, text="$a^2 + b^2 = c^2$"),
    ]
    overlays = convert_document_to_mathml_overlays(pages, converter=stub_converter)
    assert len(overlays) == 1
    assert 'data-page-index="2"' in overlays[0]


def test_text_block_helper_uses_converter(stub_converter: LatexMathMLConverter) -> None:
    result = convert_text_block_to_mathml("$x+y$", converter=stub_converter)
    assert '<math' in result
