import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

m = importlib.import_module("translate_notes")


def test_split_chunks_roundtrip():
    text = ("段落甲内容\n\n" * 500) + "结尾段落"
    chunks = m.split_chunks(text, 500)
    assert len(chunks) > 1
    assert "".join(chunks) == text
    assert all(len(c) < 600 for c in chunks[:-1])


def test_split_chunks_short_text():
    text = "# 标题\n\n正文\n"
    assert m.split_chunks(text) == [text]


def test_split_chunks_preserves_img_block():
    src = "前文\n\n<p align=\"center\">\n  <img src=\"./images/a.png\" width=\"400\">\n</p>\n\n后文\n"
    chunks = m.split_chunks(src, 40)
    assert "".join(chunks) == src


def test_valid_accepts_matching_structure():
    src = "See [doc](./a.md) and ```code``` with <img src=\"x.png\">"
    out = "见 [doc](./a.md) 和 ```code``` 含 <img src=\"x.png\">"
    assert m.valid(src, out)


def test_valid_rejects_missing_image():
    src = "text <img src=\"x.png\">"
    out = "文本"
    assert not m.valid(src, out)


def test_valid_rejects_too_short():
    src = "English sentence " * 50
    out = "短"
    assert not m.valid(src, out)


def test_valid_rejects_dropped_link():
    src = "a [x](./1.md) b [y](./2.md)"
    out = "甲 [x](./1.md) 乙"
    assert not m.valid(src, out)


def test_valid_rejects_dropped_heading():
    src = "# A\n\ntext\n\n## B\n\nmore\n"
    out = "# 甲\n\n文本\n\nmore\n"
    assert not m.valid(src, out)


def test_heading_count():
    assert m.heading_count("# a\n## b\n normal\n### c") == 3
    assert m.heading_count("no heading\n") == 0


def test_fit_boundary_keeps_newlines_between_chunks():
    src = "前文内容。\n\n"
    out = "译文。"
    fixed = m.fit_boundary(src, out)
    assert fixed == "译文。\n\n"
    assert not m.heading_count("x" + fixed + "## 标题") == 0


def test_fit_boundary_strips_model_padding():
    assert m.fit_boundary("## H\n", "  译文  \n\n") == "译文\n"


def test_fit_boundary_leading_space():
    assert m.fit_boundary("\n\n正文", "译文") == "\n\n译文"


def test_valid_rejects_glued_heading():
    src = "前文\n\n## 标题\n\n后文\n"
    out = "前文## 标题\n\n后文\n"
    assert not m.valid(src, out)


def test_glued_heading_ignores_normal_and_fence():
    assert not m.glued_heading("正文 ## 不算\n普通行\n")
    assert not m.glued_heading("```\ncode ## x\n```\n")
    assert m.glued_heading("通知给用户。## 关键优化\n")


def test_translate_file_full_heading_gate(tmp_path, monkeypatch):
    src_f = tmp_path / "README.md"
    src_f.write_text("## A\n\n正文\n\n## B\n\n尾\n", encoding="utf-8")
    out_f = tmp_path / "out.md"

    def fake_translate(content, label=""):
        return content

    monkeypatch.setattr(m, "translate", fake_translate)
    m.translate_file(src_f, out_f)
    assert m.heading_count(out_f.read_text(encoding="utf-8")) == 2

    def bad_translate(content, label=""):
        return content.replace("## B", "B")

    monkeypatch.setattr(m, "translate", bad_translate)
    import pytest

    with pytest.raises(RuntimeError):
        m.translate_file(src_f, tmp_path / "out2.md")


def test_all_chapters_have_md():
    src = Path(__file__).resolve().parent.parent
    dirs = sorted(p for p in src.glob("[0-9][0-9].*") if p.is_dir())
    if not dirs:
        pytest.skip("英文原版目录仅保留在本地工作区")
    assert len(dirs) == 28
    for d in dirs:
        assert (d / "README.md").exists() or (d / "Readme.md").exists()


def test_models_listed():
    assert len(m.MODELS) == 4
    assert m.MODELS[0].startswith("inclusionai/")


def test_main_copies_directory_assets(tmp_path, monkeypatch):
    src = tmp_path / "src"
    ch = src / "01. Demo"
    (ch / "images").mkdir(parents=True)
    (ch / "images" / "a.png").write_bytes(b"png")
    (ch / "README.md").write_text("# Demo\n", encoding="utf-8")
    (src / "README.md").write_text("index\n", encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr(m, "SRC_DIR", src)
    monkeypatch.setattr(m, "OUT_DIR", out)

    def fake_translate_file(sp, op):
        op.write_text("翻译结果\n", encoding="utf-8")

    monkeypatch.setattr(m, "translate_file", fake_translate_file)
    assert m.main() == 0
    assert (out / "01. Demo" / "images" / "a.png").exists()
    assert (out / "01. Demo" / "README.md").read_text(encoding="utf-8") == "翻译结果\n"
    assert (out / "README.md").exists()
