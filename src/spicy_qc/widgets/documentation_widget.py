from __future__ import annotations

from typing import TYPE_CHECKING

import emoji
import markdown
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

if TYPE_CHECKING:
    from spicy_qc.widgets.criterion_widget import CriterionWidget

from spicy_qc.gui.utils import get_theme

THEME = get_theme()


CSS = f"""
    body {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        line-height: 1.3;
        color: {THEME["text_color"]};
        background-color: {THEME["bg_three"]};
        max-width: 860px;
    }}

    h1, h2, h3, h4 {{
        color: {THEME["H2_color"]};
    }}

    h1 {{
        font-size: 22px;
    }}

    h2 {{
        font-size: 18px;
    }}

    h3 {{
        font-size: 16px;
    }}

    h4 {{
        font-size: 14px;
    }}

    code {{
        color: {THEME["text_color"]};
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
    }}

    pre code {{
        color: {THEME["text_color"]};
        font-family: 'Courier New', monospace;
        line-height: 1.3;
        overflow-x:auto;
        tab-width: 4;
        display: block;
    }}

    a {{
        color: {THEME["H2_color"]};
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
    }}

    th, td {{
        border: 1px solid {THEME["outline"]};
        padding: 6px;
    }}

    th {{
        background-color: {THEME["bg_four"]};
    }}

    td {{
        background-color: {THEME["bg_one"]};
    }}


    blockquote {{
        border-left: 5px solid {THEME["text_color2"]};
        color: {THEME["text_color"]};
        background-color: {THEME["text_color2"]}20;
        margin: 6px;
        padding-top: 1px;
        padding-bottom: 1px;
        padding-left: 6px;
        padding-right: 6px;
    }}

    .admonition {{
        padding-top: 1px;
        padding-bottom: 1px;
        padding-left: 6px;
        padding-right: 6px;
        border-radius: 5px;
        border-left: 3px solid;
        margin: 6px;
    }}

    .admonition-title {{
        font-weight: bold;
    }}

    .note   {{
        border-left-color: #569cd6;
        background-color: #569cd612;
    }}
    .warning {{
        border-left-color: #e8a838;
        background-color: #e8a83812;
    }}
    .tip    {{
        border-left-color: #4ec94e;
        background-color: #4ec94e12;
    }}
    .danger {{
        border-left-color: #e85050;
        background-color: #e8505012;
    }}
    .question {{
        border-left-color: #d0a000;
        background-color: #d0a00012;
    }}
    .info {{
        border-left-color: #00a0d0;
        background-color: #00a0d012;
    }}
    .example {{
        border-left-color: #a050e8;
        background-color: #a050e812;
    }}

    .result {{
        border-left-color: #aaaaaa;
        background-color: #aaaaaa12;
    }}
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


SCROLLBAR_CSS = f"""
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: {THEME["bg_two"]};
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb {{
    background: {THEME["bg_four"]};
    border-radius: 4px;
}}
"""


class DocPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        # Let the initial load through, intercept link clicks
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False  # block new page opening in the qt app
        return True


class DocumentationWidget(QWebEngineView):
    def __init__(self, criterion_widget: CriterionWidget):
        self.criterion_widget = criterion_widget
        super().__init__()
        self.setPage(DocPage(self))
        self.load_markdown()
        self.loadFinished.connect(self._inject_scrollbar_style)

    def _inject_scrollbar_style(self, ok):
        if not ok:
            return
        js = f"""
            var style = document.createElement('style');
            style.textContent = `{SCROLLBAR_CSS}`;
            document.head.appendChild(style);
        """
        self.page().runJavaScript(js)

    def load_markdown(self):
        doc_file = self.criterion_widget.criterion._source_file.with_name("documentation.md")
        md_text = self.criterion_widget.criterion.documentation
        md_text = emoji.emojize(md_text, language="alias")
        html = markdown_to_html(md_text, CSS)
        base_url = QUrl.fromLocalFile(doc_file.as_posix())
        self.setHtml(html, baseUrl=base_url)
