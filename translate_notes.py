import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODELS = [
    "inclusionai/ling-3.0-flash-fin:free",
    "qwen/qwen3.8-27b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
]

SRC_DIR = Path(__file__).parent / "system-design-notes"
OUT_DIR = Path(__file__).parent / "系统设计笔记"
MAX_CHUNK_CHARS = 5000
MAX_TOKENS = 4000
MAX_RETRY = 3
RETRY_SLEEP = 15
REQ_DELAY = 1.0

PROMPT = """你是专业翻译。把下面的 Markdown 片段翻译成简体中文，只输出翻译结果，不要任何解释或前言。

规则：
1. 保留全部 Markdown 语法结构，标题层级、列表、表格、引用、分隔线与原文一一对应。
2. HTML 标签原样保留，img 的 src、alt、width、style 等属性一律不改动。
3. 链接地址不改动，只翻译链接文字。
4. 代码、代码块、函数名、API 名、专有名词如 Kafka、Redis、CAP 保留英文。
5. 加粗等行内标记的位置与数量保持一致。
6. 技术术语翻译准确，行文自然，不要机翻腔。
7. 标题行数量与层级必须与原文完全相同，一个都不能少，不能合并或改层级。
8. 标题编号统一风格：Section N 译为第N节，Step N 译为第N步，Part N 译为第N节，数字用阿拉伯数字。

原文片段：
"""

SYSTEM = {"role": "system", "content": "你是资深技术翻译，只输出翻译结果。"}


def split_chunks(text, max_chars=MAX_CHUNK_CHARS):
    chunks = []
    buf = ""
    for line in text.splitlines(keepends=True):
        buf += line
        if len(buf) >= max_chars and not line.strip():
            chunks.append(buf)
            buf = ""
    if buf:
        chunks.append(buf)
    assert "".join(chunks) == text, "分块拼接必须与原文完全一致"
    return chunks


def api_call(model, content, max_tokens=MAX_TOKENS):
    body = {
        "model": model,
        "messages": [SYSTEM, {"role": "user", "content": PROMPT + content}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "reasoning": {"enabled": False},
    }
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + API_KEY},
    )
    resp = urllib.request.urlopen(req, timeout=300)
    data = json.load(resp)
    choice = data["choices"][0]
    text = choice["message"].get("content") or ""
    if choice["finish_reason"] != "stop":
        raise RuntimeError("finish_reason=%s 输出被截断 model=%s" % (choice["finish_reason"], model))
    if not text.strip():
        raise RuntimeError("空返回 model=%s" % model)
    return text.strip()


def translate(content, label=""):
    last_err = None
    for attempt in range(MAX_RETRY):
        for model in MODELS:
            try:
                out = api_call(model, content)
                out = fit_boundary(content, out)
                if not valid(content, out):
                    last_err = RuntimeError("结构校验失败 model=%s %s" % (model, label))
                    continue
                time.sleep(REQ_DELAY)
                return out
            except urllib.error.HTTPError as e:
                detail = e.read().decode()[:200]
                print("  %s HTTP%s %s" % (model, e.code, detail), flush=True)
                last_err = e
            except Exception as e:
                print("  %s %s" % (model, e), flush=True)
                last_err = e
            time.sleep(3)
        print("  第%d轮全模型失败，%ds 后重来" % (attempt + 1, RETRY_SLEEP), flush=True)
        time.sleep(RETRY_SLEEP)
    raise RuntimeError("翻译失败 %s: %s" % (label, last_err))


def valid(src, out):
    if len(out) < len(src) * 0.25:
        return False
    if out.count("```") != src.count("```"):
        return False
    if out.count("<img") != src.count("<img"):
        return False
    if out.count("](") != src.count("]("):
        return False
    if heading_count(out) != heading_count(src):
        return False
    if glued_heading(out):
        return False
    return True


def glued_heading(text):
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith("#"):
            continue
        for match in re.finditer(r"#{1,6}\s", line):
            i = match.start()
            if i > 0 and not line[i - 1].isspace():
                return True
    return False


def heading_count(text):
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))


def fit_boundary(src, out):
    lead = src[: len(src) - len(src.lstrip())]
    trail = src[len(src.rstrip()) :]
    return lead + out.strip() + trail


def translate_file(src_path, out_path):
    text = src_path.read_text(encoding="utf-8")
    if out_path.exists() and out_path.stat().st_size > 0:
        print("%s 已翻译，跳过" % src_path.name, flush=True)
        return
    chunks = split_chunks(text)
    print("%s -> %d 块" % (src_path.name, len(chunks)), flush=True)
    parts = []
    for i, chunk in enumerate(chunks, 1):
        print("  块 %d/%d" % (i, len(chunks)), flush=True)
        parts.append(translate(chunk, "%s#%d" % (src_path, i)))
    result = "".join(parts)
    if heading_count(result) != heading_count(text):
        raise RuntimeError(
            "全文件标题数不一致 源%d 译%d %s" % (heading_count(text), heading_count(result), src_path)
        )
    out_path.write_text(result, encoding="utf-8")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    files = sorted(p for p in SRC_DIR.glob("*") if p.is_dir() and not p.name.startswith("."))
    readme = [p for p in [SRC_DIR / "Readme.md", SRC_DIR / "README.md"] if p.exists()]
    for chapter in files:
        target = OUT_DIR / chapter.name
        target.mkdir(exist_ok=True)
        md = [p for p in [chapter / "README.md", chapter / "Readme.md"] if p.exists()]
        md_names = {p.name for p in md}
        for asset in chapter.iterdir():
            if asset.name in md_names:
                continue
            dest = target / asset.name
            if asset.is_dir():
                shutil.copytree(asset, dest, dirs_exist_ok=True)
            else:
                shutil.copy(asset, dest)
        if not md:
            print("跳过无 md 的目录 %s" % chapter.name, flush=True)
            continue
        try:
            translate_file(md[0], target / "README.md")
        except Exception as e:
            print("失败 %s: %s" % (md[0], e), file=sys.stderr, flush=True)
            return 1
    if readme:
        try:
            translate_file(readme[0], OUT_DIR / "README.md")
        except Exception as e:
            print("失败 %s: %s" % (readme[0], e), file=sys.stderr, flush=True)
            return 1
    print("完成，输出目录 %s" % OUT_DIR, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
