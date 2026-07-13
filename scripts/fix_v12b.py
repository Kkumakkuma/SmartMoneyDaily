# -*- coding: utf-8 -*-
"""
fix_v12b.py (2026-07-13, 1회용) — backfill_v12 이후 codex 지적 보완.

1) 중첩 링크 정리: [X [inner](url) Y] → [X inner Y](url)
2) 생 대괄호 참조 [Title] 해소: 실존 글 제목이면 실링크, 프루닝된 글이면 keeper 링크, 매칭 없으면 대괄호 제거
3) LaTeX 잔존 전수 변환 (\\[ ... \\], \\text, \\frac 등 → 백틱 일반 수식)
4) '## Conclusion' 헤딩 뒤 고아 H2 이동 (backfill은 'In conclusion' 문단만 처리했음)
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POSTS = os.path.join(ROOT, "_posts")
DRY = "--dry-run" in sys.argv

KEEP_AFTER_CONCL = ("further reading", "related guides", "more on this topic", "keep reading")

# backfill_v12의 프루닝 매핑 (drafted → keeper) — 생 대괄호가 프루닝된 글을 가리키면 keeper로
from backfill_v12 import PRUNE, permalink_of  # noqa: E402


def norm_title(t):
    return re.sub(r"\s+", " ", t.replace("’", "'").strip().strip('.').lower())


def build_title_map():
    m = {}
    for p in glob.glob(os.path.join(POSTS, "*.md")):
        s = io.open(p, encoding="utf-8").read()
        tm = re.search(r'(?m)^title:\s*"(.+?)"\s*$', s)
        if tm:
            m[norm_title(tm.group(1))] = "/SmartMoneyDaily" + permalink_of(os.path.basename(p))
    # 프루닝된 글 제목 → keeper URL
    drafts = os.path.join(ROOT, "_drafts")
    for fname, keeper in PRUNE.items():
        p = os.path.join(drafts, fname)
        if os.path.exists(p):
            s = io.open(p, encoding="utf-8").read()
            tm = re.search(r'(?m)^title:\s*"(.+?)"\s*$', s)
            if tm:
                m[norm_title(tm.group(1))] = "/SmartMoneyDaily" + permalink_of(keeper)
    return m


NESTED = re.compile(r"\[([^\[\]]*)\[([^\]]+)\]\(([^)]+)\)([^\]]*)\]")
BARE = re.compile(r"\[([^\[\]\n]{10,120})\](?!\()")
LATEX_LINE = re.compile(r"\\\[(.+?)\\\]", re.S)


def clean_latex_expr(expr):
    e = expr
    e = re.sub(r"\\text\{([^}]*)\}", r"\1", e)
    e = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", e)
    e = e.replace(r"\left", "").replace(r"\right", "")
    e = re.sub(r"\^\{([^}]*)\}", r"^\1", e)
    e = e.replace(r"\times", "x").replace("\\", "")
    e = re.sub(r"\s+", " ", e).strip()
    return "`" + e + "`"


def move_orphans_after_conclusion_heading(body):
    m = None
    for m in re.finditer(r"(?m)^## Conclusion[^\n]*$", body):
        pass
    if not m:
        return body, False
    # 결론 헤딩 섹션 = 헤딩부터 다음 H2 전까지
    start = m.start()
    nxt = re.search(r"\n## ", body[m.end():])
    if not nxt:
        return body, False
    concl_end = m.end() + nxt.start()
    concl_block = body[start:concl_end]
    rest = body[concl_end:]
    blocks = [b for b in re.split(r"(?=\n## )", rest) if b.strip()]
    move, keep = [], []
    for b in blocks:
        hm = re.match(r"\n## ([^\n]+)", b)
        h = hm.group(1).strip().lower() if hm else ""
        (keep if any(k in h for k in KEEP_AFTER_CONCL) else move).append(b)
    if not move:
        return body, False
    new = (body[:start].rstrip() + "\n" + "".join(mb.rstrip() + "\n" for mb in move)
           + "\n" + concl_block.strip("\n") + "\n" + "".join(keep))
    return new.rstrip() + "\n", True


def main():
    titles = build_title_map()
    stats = {"nested": 0, "linked": 0, "stripped": 0, "latex": 0, "concl": 0}
    for p in sorted(glob.glob(os.path.join(POSTS, "*.md"))):
        s = io.open(p, encoding="utf-8").read()
        orig = s

        # 1) 중첩 링크: [X [inner](url) Y] → [X inner Y](url)
        def _nested(m):
            stats["nested"] += 1
            text = re.sub(r"\s+", " ", (m.group(1) + m.group(2) + m.group(4)).strip())
            return f"[{text}]({m.group(3)})"
        s = NESTED.sub(_nested, s)

        # 2) 생 대괄호 참조
        def _bare(m):
            t = m.group(1)
            url = titles.get(norm_title(t))
            if url:
                stats["linked"] += 1
                return f"[{t}]({url})"
            # 이미지/각주/일반 대괄호 표현 보호: 제목처럼 보일 때만(첫 글자 대문자 + 단어 3개+) 제거
            if t[0].isupper() and len(t.split()) >= 3:
                stats["stripped"] += 1
                return t
            return m.group(0)
        s = BARE.sub(_bare, s)

        # 3) LaTeX 잔존
        if "\\[" in s or "\\text" in s or "\\frac" in s:
            s2 = LATEX_LINE.sub(lambda m: clean_latex_expr(m.group(1)), s)
            # 남은 인라인 \( ... \)
            s2 = re.sub(r"\\\((.+?)\\\)", lambda m: clean_latex_expr(m.group(1)), s2)
            if s2 != s:
                stats["latex"] += 1
            s = s2

        # 4) ## Conclusion 헤딩 뒤 고아 섹션
        fm = re.match(r"^(---\n.*?\n---\n)(.*)$", s, re.S)
        if fm:
            body, moved = move_orphans_after_conclusion_heading(fm.group(2))
            if moved:
                stats["concl"] += 1
                s = fm.group(1) + body

        if s != orig and not DRY:
            io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(("DRY-RUN " if DRY else "") + "fix_v12b done:", stats)


if __name__ == "__main__":
    main()
