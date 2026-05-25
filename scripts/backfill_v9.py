# -*- coding: utf-8 -*-
"""v9 backfill (2026-05-26): 이미 발행된 _posts 글 일괄 정정 (애드센스 재승인).
- 내부링크 /slug/ → 실제 permalink /SmartMoneyDaily/Y/M/D/slug/ (기존 404 수정)
- About the Author 단락 → 고정 텍스트(1인칭 통일, Last reviewed=각 글 발행월)
- frontmatter description에 양산 BANNED 단어가 있으면 generate_meta_description 재생성(키 필요)
한 번만 돌리는 일회성. 변경된 파일만 다시 쓴다.
"""
import os
import re
import glob

import generate_post as g

BLOG = "SmartMoneyDaily"
ROOT = g.get_repo_root()
POSTS = os.path.join(ROOT, "_posts")
HAS_KEY = bool(os.environ.get("OPENAI_API_KEY"))
MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

# slug → 실제 permalink url 매핑 (전체 글)
slug_to_url = {}
file_meta = {}
for path in glob.glob(os.path.join(POSTS, "*.md")):
    fn = os.path.basename(path)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", fn)
    if not m:
        continue
    y, mo, d, slug = m.groups()
    slug_to_url[slug] = f"/{BLOG}/{y}/{mo}/{d}/{slug}/"
    file_meta[path] = (y, mo, d, slug)


_META_REPLACE = [
    (r"\bUnlock\b", "Understand"),
    (r"\bDiscover\b", "Understand"),
    (r"\bExplore\b", "Compare"),
    (r"\bDive into\b", "Look at"),
    (r"\bBoost your\b", "Grow your"),
    (r"\bBoost\b", "Grow"),
    (r"\bMaximize your\b", "Make the most of your"),
    (r"\bMaximize\b", "Make the most of"),
    (r"\bmaximizing\b", "making the most of"),
    (r"\s*[—–-]?\s*don['’]?t miss out.*$", ""),
    (r"\bLearn everything\b", "Learn"),
    (r"\bthe secrets\b", "the essentials"),
]


def despam_meta(desc):
    out = desc
    for pat, rep in _META_REPLACE:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", out).strip()


def about_block(month_year):
    return (
        "## About the Author\n\n"
        "I'm Kkuma Park, an independent writer and developer based in Seoul. I compile and explain "
        "publicly available U.S. deposit-account information — high-yield savings accounts, CDs, and "
        "money market accounts — in plain English, and I cite primary sources like the FDIC, the Federal "
        "Reserve, and the CFPB so you can verify everything yourself. I use AI tools to help draft and "
        "structure articles, and I check them against those public sources before publishing; I don't claim "
        "personal banking results I didn't have.\n\n"
        f"Last reviewed: {month_year}."
    )


changed = 0
meta_done = 0
meta_despammed = 0
link_fixed = 0
about_fixed = 0

for path, (y, mo, d, slug) in sorted(file_meta.items()):
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    orig = txt

    fm_match = re.match(r"^(---\n.*?\n---\n)(.*)$", txt, re.DOTALL)
    if not fm_match:
        print(f"  [skip] no frontmatter: {os.path.basename(path)}")
        continue
    fm, body = fm_match.group(1), fm_match.group(2)
    title_m = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.MULTILINE)
    title = title_m.group(1) if title_m else ""

    # 1) 내부링크 /slug/ → permalink (단일 세그먼트 소문자 slug만; /about/ 등 페이지·이미 고친 링크는 보호)
    def link_repl(m2):
        s = m2.group(1)
        if s in slug_to_url:
            return "](" + slug_to_url[s] + ")"
        return m2.group(0)
    new_body, n_links = re.subn(r"\]\(/([a-z0-9][a-z0-9-]*)/\)", link_repl, body)
    if n_links and new_body != body:
        body = new_body

    # 2) About the Author 단락 → 고정(각 글 발행월)
    blk = about_block(f"{MONTHS[int(mo)]} {y}")
    if re.search(r"^##\s+About the Author\b", body, flags=re.MULTILINE | re.IGNORECASE):
        new_body2, n_ab = re.subn(r"^##\s+About the Author\b.*?(?=\n##\s|\Z)",
                                  lambda _m: blk, body, count=1,
                                  flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
        if n_ab and new_body2 != body:
            body = new_body2
            about_fixed += 1

    # 3) 메타 재생성 (BANNED 단어 있을 때만)
    desc_m = re.search(r'^description:\s*"(.*)"\s*$', fm, re.MULTILINE)
    if desc_m:
        desc = desc_m.group(1)
        if any(b in desc.replace("’", "'").lower() for b in g._BANNED_META):
            if HAS_KEY and title:
                new_desc = g.generate_meta_description(title).replace('"', "'")
                meta_done += 1
            else:
                new_desc = despam_meta(desc).replace('"', "'")
                meta_despammed += 1
            if len(new_desc) > 160:
                new_desc = new_desc[:157].rsplit(" ", 1)[0] + "..."
            fm = fm[:desc_m.start(1)] + new_desc + fm[desc_m.end(1):]

    txt = fm + body
    if txt != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        changed += 1
        if n_links:
            link_fixed += 1
        print(f"  updated: {os.path.basename(path)} (links~{n_links})")

print(f"\n=== Backfill summary ===")
print(f"files changed: {changed}/{len(file_meta)}")
print(f"link-fix files: {link_fixed} | about-fix: {about_fixed} | meta-regen(GPT): {meta_done} | meta-despam(no key): {meta_despammed}")
