"""防回归：译文中正文与表格、围栏粘连导致的渲染丢失。"""

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent / "系统设计笔记"
FENCE = re.compile(r"^\s*```(.*)$")
LANG = re.compile(r"[A-Za-z0-9_+#.-]+")


def chapter_files():
    files = sorted(ROOT.glob("[0-9][0-9].*/README.md"))
    if not files:
        pytest.skip("无中文章节目录")
    return files


def table_blocks(lines):
    i = 0
    while i < len(lines):
        if re.match(r"^\s*\|", lines[i]):
            j = i
            while j < len(lines) and re.match(r"^\s*\|", lines[j]):
                j += 1
            yield i + 1, lines[i:j]
            i = j
        else:
            i += 1


def count_cells(row):
    return len(re.split(r"(?<!\\)\|", row.strip().strip("|")))


def test_table_rows_do_not_exceed_header_columns():
    """数据行单元格多于表头时，多出的内容会被 markdown-it 静默丢弃。"""
    violations = []
    for f in chapter_files():
        lines = f.read_text(encoding="utf8").splitlines()
        for lineno, block in table_blocks(lines):
            if len(block) < 2 or not re.match(r"^\s*\|[\s:|-]+\|\s*$", block[1]):
                continue
            header = count_cells(block[0])
            for row in block[2:]:
                if count_cells(row) > header:
                    violations.append(
                        f"{f.parent.name}:{lineno} 单元格 {count_cells(row)} > 表头 {header}"
                    )
    assert not violations, "表格行比表头多出单元格，超出部分会丢正文：\n" + "\n".join(violations)


def test_code_fence_lines_are_well_formed():
    """闭合围栏粘连文字会让其后整段正文被渲染成一个大代码块。"""
    violations = []
    for f in chapter_files():
        lines = f.read_text(encoding="utf8").splitlines()
        in_fence = False
        for n, line in enumerate(lines, 1):
            m = FENCE.match(line)
            if not m:
                continue
            info = m.group(1).strip()
            if in_fence:
                if info:
                    violations.append(f"{f.parent.name}:{n} 闭合围栏粘连文字 {info[:40]}")
                in_fence = False
            else:
                if info and not LANG.fullmatch(info):
                    violations.append(f"{f.parent.name}:{n} 围栏信息串异常 {info[:40]}")
                in_fence = True
        if in_fence:
            violations.append(f"{f.parent.name} 存在未闭合围栏")
    assert not violations, "围栏语法异常：\n" + "\n".join(violations)
