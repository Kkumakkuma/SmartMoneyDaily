# -*- coding: utf-8 -*-
"""v11 backfill (2026-06-10): 기존 _posts 전체에서 '## About the Author' 고정 단락 제거.

배경: 41편 모두 동일한 About the Author 단락 반복 = 양산 시그니처 (codex 지적).
저자 표기는 _layouts/post.html author-box 하나로 단일화하고,
신선도 신호는 '*Last reviewed: <발행월> by Kkuma Park.*' 한 줄로 대체.

사용:
  python scripts/backfill_v11_about.py           # dry-run (변경 대상만 출력)
  python scripts/backfill_v11_about.py --apply   # 실제 적용
"""
import os
import re
import sys

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

ABOUT_PAT = re.compile(r"\n*^##\s+About the Author\b.*?(?=\n##\s|\Z)",
                       re.DOTALL | re.MULTILINE | re.IGNORECASE)
REVIEWED_TAIL_PAT = re.compile(r"\*Last reviewed:.*?\*\s*$", re.IGNORECASE)


def main():
    apply = "--apply" in sys.argv
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posts_dir = os.path.join(repo_root, "_posts")

    changed, skipped = 0, 0
    for fn in sorted(os.listdir(posts_dir)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(posts_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        m = re.match(r"(\d{4})-(\d{2})-\d{2}-", fn)
        if not m:
            print(f"  ? 날짜 파싱 실패 스킵: {fn}")
            skipped += 1
            continue
        year, month = int(m.group(1)), int(m.group(2))
        reviewed_line = f"*Last reviewed: {MONTHS[month]} {year} by Kkuma Park.*"

        if not ABOUT_PAT.search(text):
            # About 없으면 Last reviewed 한 줄만 보장
            if REVIEWED_TAIL_PAT.search(text.rstrip()):
                skipped += 1
                continue
            new_text = text.rstrip() + "\n\n" + reviewed_line + "\n"
            print(f"  + Last reviewed만 추가: {fn}")
        else:
            new_text = ABOUT_PAT.sub("", text)
            new_text = new_text.rstrip() + "\n\n" + reviewed_line + "\n"
            print(f"  - About 제거 + Last reviewed: {fn}")

        changed += 1
        if apply:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_text)

    mode = "APPLIED" if apply else "DRY-RUN"
    print(f"\n[{mode}] 변경 {changed} / 스킵 {skipped}")
    if not apply and changed:
        print("실제 적용: python scripts/backfill_v11_about.py --apply")


if __name__ == "__main__":
    main()
