from pathlib import Path

import markdown
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

CSS = """
    body {
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #e0e0e0;
        background-color: #1e1e1e;
        max-width: 860px;
        margin: 40px auto;
        padding: 0 20px;
    }

    h1, h2, h3 {
        color: #ffffff;
        border-bottom: 1px solid #444;
        padding-bottom: 4px;
    }

    code {
        background-color: #2d2d2d;
        color: #ce9178;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }

    pre {
        background-color: #2d2d2d;
        padding: 12px;
        border-radius: 5px;
        border-left: 3px solid #569cd6;
        overflow-x: auto;
    }

    pre code {
        background: none;
        padding: 0;
        border-radius: 0;
        color: #d4d4d4;
    }

    a {
        color: #569cd6;
    }

    blockquote {
        border-left: 4px solid #569cd6;
        margin: 0;
        padding-left: 16px;
        color: #888;
    }

    table {
        border-collapse: collapse;
        width: 100%;
    }

    th, td {
        border: 1px solid #444;
        padding: 8px 12px;
    }

    th {
        background-color: #2d2d2d;
    }

    .admonition {
        padding: 10px 16px;
        border-radius: 5px;
        border-left: 4px solid #888;
        margin: 16px 0;
    }

    .admonition-title {
        font-weight: bold;
        margin-bottom: 4px;
    }

    .note   { border-left-color: #569cd6; background-color: #1a2a3a; }
    .note   .admonition-title { color: #569cd6; }
    .warning { border-left-color: #e8a838; background-color: #2a2010; }
    .warning .admonition-title { color: #e8a838; }
    .tip    { border-left-color: #4ec94e; background-color: #0f2a0f; }
    .tip    .admonition-title { color: #4ec94e; }
    .danger { border-left-color: #e85050; background-color: #2a1010; }
    .danger .admonition-title { color: #e85050; }
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
    def __init__(self, criterion_widget):
        super().__init__(parent)
        self.load_markdown

    def load_markdown(self, path: str):
        text = Path(path).read_text(encoding="utf-8")
        html = markdown_to_html(text, CSS)
        base_url = QUrl.fromLocalFile(str(Path(path).resolve().parent) + "/")
        self.setHtml(html, baseUrl=base_url)


app = QApplication()

widget = QWidget()
layout = QVBoxLayout(widget)
web = DocumentationWidget()
web.load_markdown(r"D:\gitWorkspace\spicy_qc\src\spicy_qc\example_criterions\criterion_with_warnings\documentation.md")
layout.addWidget(web)

widget.show()

app.exec()
