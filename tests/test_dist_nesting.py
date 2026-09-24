"""产物级校验：p 标签内不得嵌套块级标签，否则 dev 会报水合警告。"""

import pathlib
import re

import pytest

DIST = pathlib.Path(__file__).resolve().parent.parent / ".vitepress" / "dist"
TOKEN = re.compile(
    r"<(/?)(p|div|ul|ol|table|blockquote|pre|li|dl|hr|section|header|footer|details|figure|h[1-6])(?=[\s/>])",
    re.I,
)


def dist_pages():
    pages = sorted(DIST.rglob("index.html")) if DIST.exists() else []
    if not pages:
        pytest.skip("无构建产物")
    return pages


def test_no_block_tags_nested_inside_paragraph():
    violations = []
    for page in dist_pages():
        html = page.read_text(encoding="utf8")
        depth = 0
        for m in TOKEN.finditer(html):
            closing, tag = m.group(1), m.group(2).lower()
            if tag == "p":
                depth = max(0, depth - (1 if closing else -1))
                continue
            if not closing and depth > 0:
                ctx = re.sub(r"\s+", " ", html[max(0, m.start() - 60):m.start() + 60])
                violations.append(f"{page.parent.name}: <{tag}> 嵌套于 <p> 内 | {ctx}")
    assert not violations, "存在 p 套块级标签的非法结构：\n" + "\n".join(violations)
