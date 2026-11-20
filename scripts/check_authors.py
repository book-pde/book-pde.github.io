#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AUTHORS_YML = ROOT / "authors.yml"
BOOK_DIR = ROOT / "book"


def load_known_authors(path: Path) -> set[str]:
    known: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^-\s*id\s*:\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*$", line)
        if m:
            known.add(m.group(1))
    return known


def parse_frontmatter_authors(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    if end == -1:
        return []
    fm = text[4:end]
    lines = fm.splitlines()

    authors: list[str] = []
    in_authors = False

    for line in lines:
        if re.match(r"^authors\s*:\s*$", line.strip()):
            in_authors = True
            continue

        if in_authors:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^  -\s*([A-Za-z0-9_-]+)\s*$", line)
            if m:
                authors.append(m.group(1))
                continue
            m = re.match(r"^  -\s*id\s*:\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*$", line)
            if m:
                authors.append(m.group(1))
                continue
            if line.startswith("    "):
                continue
            break

    return authors


def main() -> int:
    if not AUTHORS_YML.exists():
        print(f"ERROR: {AUTHORS_YML} not found")
        return 1

    known = load_known_authors(AUTHORS_YML)
    if not known:
        print("ERROR: No known author IDs found in authors.yml")
        return 1

    bad: list[str] = []

    for md in sorted(BOOK_DIR.rglob("*.md")):
        rel = md.relative_to(ROOT).as_posix()
        if "/_snippets/" in rel:
            continue

        text = md.read_text(encoding="utf-8")
        for aid in parse_frontmatter_authors(text):
            if aid not in known:
                bad.append(f"{rel}: unknown author id '{aid}'")

    if bad:
        print("Author check failed:")
        for item in bad:
            print(f"- {item}")
        return 1

    print("Author check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
