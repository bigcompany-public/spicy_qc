from __future__ import annotations

from typing import TYPE_CHECKING

import markdown
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

if TYPE_CHECKING:
    from spicy_qc.widgets.criterion_widget import CriterionWidget

from spicy_qc.gui.utils import get_theme

THEME = get_theme()


CSS = f"""
    body {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        line-height: 1;
        color: {THEME["text_color"]};
        background-color: {THEME["bg_three"]};
        max-width: 860px;
    }}

    h1, h2, h3 {{
        color: {THEME["H2_color"]};
        border-bottom: 1px solid {THEME["outline2"]};
        padding-bottom: 2px;
    }}

    code {{
        color: {THEME["error"]};
        background-color: {THEME["bg_two"]};
        padding-top: 3px;
        padding-bottom: 3px;
        padding-left: 6px;
        padding-right: 6px;
        border-radius: 3px;
    }}

    pre {{
        background-color: {THEME["bg_two"]};
        padding: 12px;
        border-radius: 3px;
        border-left: 1px solid {THEME["text_color"]};
        overflow-x: auto;
    }}

    pre code {{
        color: {THEME["text_color"]};
        font-family: 'Courier New', monospace;
    }}

    a {{
        color: #569cd6;
    }}

    blockquote {{
        border-left: 4px solid #569cd6;
        margin: 0;
        padding-left: 16px;
        color: #888;
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
    }}

    th, td {{
        border: 1px solid #444;
        padding: 8px 12px;
    }}

    th {{
        background-color: #2d2d2d;
    }}

    .admonition {{
        padding: 10px 16px;
        border-radius: 5px;
        border-left: 4px solid #888;
        margin: 16px 0;
    }}

    .admonition-title {{
        font-weight: bold;
        margin-bottom: 4px;
    }}

    .note   {{ border-left-color: #569cd6; background-color: #1a2a3a; }}
    .note   .admonition-title {{ color: #569cd6; }}
    .warning {{ border-left-color: #e8a838; background-color: #2a2010; }}
    .warning .admonition-title {{ color: #e8a838; }}
    .tip    {{ border-left-color: #4ec94e; background-color: #0f2a0f; }}
    .tip    .admonition-title {{ color: #4ec94e; }}
    .danger {{ border-left-color: #e85050; background-color: #2a1010; }}
    .danger .admonition-title {{ color: #e85050; }}
"""


def markdown_to_html(md_text: str, css: str) -> str:
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc", "admonition", "attr_list", "nl2br"])
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""


class DocumentationWidget(QWebEngineView):
    def __init__(self, criterion_widget: CriterionWidget):
        self.criterion_widget = criterion_widget
        super().__init__()
        self.load_markdown()

    def load_markdown(self):
        doc_file = self.criterion_widget.criterion._source_file.with_name("documentation.md")
        md_text = self.criterion_widget.criterion.documentation
        html = markdown_to_html(md_text, CSS)
        base_url = QUrl.fromLocalFile(doc_file.as_posix())
        self.setHtml(html, baseUrl=base_url)
