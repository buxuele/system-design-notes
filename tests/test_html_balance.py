import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "系统设计笔记"
VOID = {"img", "br", "hr", "input", "col", "source", "wbr", "embed", "track", "area", "base", "link", "meta"}
FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: closing </{tag}> without opening")
            return
        if self.stack[-1][0] != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: closing </{tag}> but innermost open is <{self.stack[-1][0]}> from line {self.stack[-1][1][0]}"
            )
            while self.stack and self.stack[-1][0] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
            return
        self.stack.pop()


def strip_code(text: str) -> str:
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def check(path: Path):
    parser = Balance()
    parser.feed(strip_code(path.read_text(encoding="utf8")))
    for tag, pos in parser.stack:
        parser.errors.append(f"line {pos[0]}: unclosed <{tag}>")
    return parser.errors


def main():
    bad = 0
    for md in sorted(ROOT.rglob("*.md")):
        for err in check(md):
            bad += 1
            print(f"{md.relative_to(ROOT)}: {err}")
    print(f"files={len(list(ROOT.rglob('*.md')))} errors={bad}")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
