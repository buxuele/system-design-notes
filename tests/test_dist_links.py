import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

DIST = Path(__file__).resolve().parents[1] / ".vitepress" / "dist"


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.refs.append(value)


def main():
    if not DIST.is_dir():
        print("dist 目录不存在，先执行 npm run build")
        return 1

    html_files = sorted(DIST.rglob("*.html"))
    bad = []
    checked = 0
    for page in html_files:
        parser = Links()
        parser.feed(page.read_text(encoding="utf8"))
        for ref in parser.refs:
            parsed = urlparse(ref)
            if parsed.scheme or ref.startswith("//") or ref.startswith("#"):
                continue
            target = unquote(parsed.path)
            if not target:
                continue
            checked += 1
            resolved = (DIST / target.lstrip("/")) if target.startswith("/") else (page.parent / target)
            resolved = resolved.resolve()
            candidate = resolved
            if resolved.is_dir():
                candidate = resolved / "index.html"
            if not candidate.exists():
                bad.append(f"{page.relative_to(DIST)} -> {ref}")

    for item in bad:
        print("死链:", item)
    print(f"pages={len(html_files)} refs={checked} dead={len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
