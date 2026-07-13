"""
SmartMoneyDaily Auto Post Generator v8 (2026-05-23) — AdSense re-approval rebuild
- Single narrow niche: high-yield savings, CDs, money market accounts (US)
- ACCURACY FIRST: no fabricated numbers, dates, personal results, or current APYs
- Public 1st-party sources (FDIC / Federal Reserve / CFPB / NCUA / Treasury) by name
- used_topics.json prevents duplicate content; internal linking kept for SEO
"""

from openai import OpenAI
import datetime
import json
import os
import random
import re
import time

BLOG_NAME = "SmartMoneyDaily"
BLOG_NICHE = "high-yield savings accounts, CDs, and money market accounts"
BLOG_DESCRIPTION = "Plain-English guides to high-yield savings accounts, CDs, and money market accounts, built from public FDIC and Federal Reserve information."

CATEGORIES = [
    "high-yield-savings",     "cd-rates",     "money-market",     "fdic-insurance",
    "savings-strategy",     "bank-comparison",     "interest-rates",     "emergency-fund",
]

# {YEAR} is a literal placeholder; it is substituted at call time (see _generate_post_content_inner).
SYSTEM_PROMPT = """You are a personal finance writer for SmartMoneyDaily, a site focused narrowly on
high-yield savings accounts (HYSAs), certificates of deposit (CDs), and money market accounts in the United States.

Your job: write accurate, genuinely useful, AdSense-quality explainers that a careful reader can trust —
written like a knowledgeable human, not generic AI filler.

ACCURACY — THE #1 RULE (this is exactly what gets finance sites approved or rejected):
- Do NOT invent specific dollar amounts, dates, personal results, account names, or test outcomes.
- Do NOT fabricate a personal anecdote (e.g. "In 2023 I moved $4,200 into..."). If you did not do it, do not claim it.
- Use ONLY:
  (a) general facts stated as ranges or typical behavior ("online banks usually pay meaningfully more than the national average"),
  (b) named public reference points that are stable and verifiable (FDIC standard deposit insurance is $250,000 per depositor,
      per insured bank, per ownership category; the FDIC publishes national-average deposit rates; the Federal Reserve sets the
      federal funds rate; NCUA insures credit unions),
  (c) clearly hypothetical examples explicitly labeled ("For example, if you kept $10,000 in an account earning 4% APY,
      that would be about $400 in a year before tax").
- Never state a specific CURRENT APY as a fact (rates change constantly). Instead explain how to find and compare current rates.
- Do NOT state a numeric pass-through ratio between Federal Reserve rate moves and account APYs (e.g., "a 0.25% Fed hike adds about 0.1-0.3% to your APY"). No authority publishes such a fixed ratio and it cannot be verified. Describe the relationship qualitatively only (when the Fed raises rates, deposit yields generally tend to rise too, but the timing and amount vary by institution).
- All examples and references must be consistent with the current year {YEAR}. Never cite a past personal result with a specific date.
- Accuracy note: the Federal Reserve suspended Regulation D's six-per-month savings/money-market withdrawal limit in 2020.
  Do NOT present a federal "six withdrawals per month" rule as if it is current. Describe withdrawal limits as set by each
  individual bank or credit union (some still impose their own limits).
- Do NOT use promotional or promissory phrasing such as "guaranteed returns", "risk-free profit", or "you will earn".
  A CD pays a fixed, contractual interest rate and (within FDIC limits) protects principal — describe that precisely as a
  "fixed interest rate" or "guaranteed interest rate", never as "guaranteed returns" on an "investment".

Writing rules:
- Friendly, clear, authoritative tone. Short paragraphs (2-3 sentences).
- Use ## for H2 and ### for H3. Bullet/numbered lists where they aid comprehension.
- Naturally use the main keyword 4-6 times — no keyword stuffing.
- Open with a concrete, specific hook (a common mistake, a number that is generally true, or the core question) —
  never a generic "In today's world" intro.
- End with a clear, actionable next step.
- Do NOT output a markdown "# Title". Do NOT add AI disclaimers or an "About the Author" section inside the article body (author info and the transparency note are shown by the site layout, not inside the article).

ANTI-AI-CLICHE (these phrases trigger reviewers' "low-value AI" flag — never use):
- "In today's fast-paced world", "In the modern era", "It's no secret that", "Have you ever wondered",
  "Welcome to my blog", "Let's dive in", "delve into", "navigate the world of", "unlock the secrets",
  "embark on a journey", "treasure trove", "in the realm of", "tapestry of", "ever-evolving landscape",
  "in today's market", "when it comes to", "the world of personal finance", "navigating the complexities",
  "can feel daunting", "can feel overwhelming".
- Avoid empty filler: "It is important to note that", "It goes without saying", "Needless to say".

VOICE / E-E-A-T (honest version — do NOT fabricate):
- You may use a light editorial first-person voice to show judgment ("Here's how I'd compare them", "What I'd check first",
  "In my view") — but NEVER invented personal financial results or fake test stories.
- Demonstrate expertise through accurate explanation of mechanics (how APY compounding works, how CD early-withdrawal
  penalties work, how FDIC coverage is calculated across ownership categories), not through made-up anecdotes.

SOURCES (build trust without fabrication):
- Reference real, well-known public authorities by name where relevant: FDIC, the Federal Reserve, the Consumer Financial
  Protection Bureau (CFPB), the U.S. Treasury, the National Credit Union Administration (NCUA). Cite what each one actually
  provides ("the FDIC's BankFind Suite lets you confirm a bank is insured").
- Do NOT fabricate URLs, study titles, or specific statistics. Name the organization and what it does; never invent a number
  and attribute it to them.

INFORMATION GAIN (make it genuinely more useful than a thin AI page):
- Prefer concrete mechanics (how compounding is calculated step by step, how a CD penalty is computed,
  how FDIC coverage stacks across ownership categories) over abstract advice anyone could write.
- When the STRUCTURE PLAN asks for a comparison table, compare real, stable attributes
  (e.g., liquidity, how the rate behaves, FDIC coverage, best use case) — each cell a short complete phrase.

STRUCTURE:
- Follow the STRUCTURE PLAN in the user message for THIS article exactly. Articles on this site
  intentionally vary in structure — do NOT fall back to one fixed skeleton you used before.
- Never output a markdown "# Title" line, and never add an "About the Author" section in the body
  (author info is rendered by the site layout; repeating it in every article is a mass-production signal).
"""


def _openai_retry(call, attempts=3, backoff=2.0):
    """OpenAI 일시 오류(rate limit, 5xx, 네트워크)에 재시도. 마지막 실패는 예외 그대로."""
    last = None
    for i in range(attempts):
        try:
            return call()
        except Exception as e:
            last = e
            if i < attempts - 1:
                time.sleep(backoff ** i)
    raise last


def get_repo_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def load_used_topics():
    """Load previously used topic slugs."""
    filepath = os.path.join(get_repo_root(), "scripts", "used_topics.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_used_topics(topics):
    filepath = os.path.join(get_repo_root(), "scripts", "used_topics.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)


def get_existing_slugs():
    """Get all existing post slugs from _posts/."""
    posts_dir = os.path.join(get_repo_root(), "_posts")
    slugs = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith(".md"):
                # Remove date prefix and .md suffix
                slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename[:-3])
                # Normalize: remove trailing random numbers
                slug = re.sub(r"-\d{2,3}$", "", slug)
                slugs.add(slug)
    return slugs


def get_recent_posts_for_linking(limit=10):
    """Return list of dicts {title, slug, url} for internal linking context.
    url은 실제 permalink(/{BLOG}/:year/:month/:day/:title/) — slug만으로 링크하면 404 (permalink가 날짜 포함)."""
    posts_dir = os.path.join(get_repo_root(), "_posts")
    posts = []
    if os.path.exists(posts_dir):
        files = sorted(os.listdir(posts_dir), reverse=True)
        for filename in files[:limit]:
            m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", filename)
            if not m:
                continue
            y, mo, d, slug = m.groups()
            url = f"/{BLOG_NAME}/{y}/{mo}/{d}/{slug}/"
            filepath = os.path.join(posts_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                        posts.append({"title": title, "slug": slug, "url": url})
                        break
    return posts


def get_recent_titles(limit=10):
    return [p["title"] for p in get_recent_posts_for_linking(limit)]


# inject_internal_links v2 (2026-04-21): exact title + partial-phrase match + Further Reading fallback
def inject_internal_links(content, recent_posts, min_links=3, max_links=5):
    """Weave internal links into the post. Strategy:
    1) Exact title match → wrap in a Markdown link
    2) If title didn't appear verbatim, try the first 3-5 meaningful words as a phrase
    3) If total inserted links < min_links, append a '## Further Reading' list at the end
    """
    if not recent_posts:
        return content

    inserted_slugs = set()
    STOPWORDS = {"the", "a", "an", "for", "and", "with", "to", "of", "in", "on", "at", "is", "are", "my"}

    def already_linked(url):
        return f"]({url})" in content

    # Pass 1: exact title
    for rp in recent_posts:
        if len(inserted_slugs) >= max_links:
            break
        title = rp.get("title", "")
        slug = rp.get("slug", "")
        url = rp.get("url", "")
        if not title or not slug or not url or already_linked(url):
            continue
        if title not in content:
            continue
        safe_title = re.escape(title)
        pattern = re.compile(r"(?<!\]\()(?<!\[)" + safe_title + r"(?!\])")
        new_content, n = pattern.subn(f"[{title}]({url})", content, count=1)
        if n:
            content = new_content
            inserted_slugs.add(slug)

    # Pass 2: partial phrase (first 3-5 meaningful words, case-insensitive)
    for rp in recent_posts:
        if len(inserted_slugs) >= max_links:
            break
        title = rp.get("title", "")
        slug = rp.get("slug", "")
        url = rp.get("url", "")
        if not title or not slug or not url or slug in inserted_slugs or already_linked(url):
            continue
        words = [w for w in re.findall(r"[A-Za-z0-9']+", title)
                 if w.lower() not in STOPWORDS and len(w) > 1]
        if len(words) < 3:
            continue
        for window in (5, 4, 3):
            if len(words) < window:
                continue
            phrase_words = words[:window]
            phrase_pattern = r"(?<!\]\()(?<!\[)" + r"\s+".join(map(re.escape, phrase_words)) + r"(?!\])"
            m = re.search(phrase_pattern, content, flags=re.IGNORECASE)
            if m:
                matched = m.group(0)
                content = content[: m.start()] + f"[{matched}]({url})" + content[m.end():]
                inserted_slugs.add(slug)
                break

    # Fallback: append Further Reading if we still don't have enough links
    if len(inserted_slugs) < min_links:
        remaining = [rp for rp in recent_posts
                     if rp.get("slug") and rp.get("url") and rp["slug"] not in inserted_slugs
                     and not already_linked(rp["url"])]
        need = max(min_links - len(inserted_slugs), 3)
        picks = remaining[:need]
        if picks:
            block = "\n\n## Further Reading\n\n"
            for rp in picks:
                block += f"- [{rp['title']}]({rp['url']})\n"
            content = content.rstrip() + block

    return content


def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


# === v8 explainer patterns (2026-05-23) ==========================
# Informational / comparison angles only — no fake "I tried X for 30 days" buyer-intent listicles.
TITLE_PATTERNS = [
    "How does a [thing] work?",
    "What is [thing] and how is it calculated?",
    "[Thing A] vs [Thing B]: which fits [situation]?",
    "How to compare [thing] without getting burned",
    "Is a [thing] worth it right now?",
    "Common mistakes with [thing] (and how to avoid them)",
    "How [thing] is taxed / what happens when rates change",
    "A beginner's guide to [thing]",
]
PATTERN_PREFIXES = ["how", "what", "is", "common", "a beginner", "the", "why", "should"]

STOPWORDS_TITLE = {
    "the","a","an","for","and","with","to","of","in","on","at","is","are","my","best","top","how","what",
    "your","this","that","its","it","be","by","or","as","you","not","do","does","worth","real","experience",
    "comparison","review","reviews","under","comparing","help","guide","tips","ultimate","cost","price",
    "prices","most","new","more","than","compare","which","when","where","who","why","ranked",
}


def _title_words(s):
    return [w.lower() for w in re.findall(r"[A-Za-z0-9']+", s) if w.lower() not in STOPWORDS_TITLE and len(w) > 2]


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    A, B = set(a), set(b)
    return len(A & B) / max(len(A | B), 1)


def _recent_keywords(used_topics, window=14, top_n=6):
    from collections import Counter
    bag = Counter()
    for t in used_topics[-window:]:
        for w in _title_words(t):
            bag[w] += 1
    return [w for w, _ in bag.most_common(top_n)]


def _pattern_of(title):
    s = title.lower().strip()
    if " vs " in s:
        return "vs"
    for p in PATTERN_PREFIXES:
        if s.startswith(p + " "):
            return p
    return "other"


def _least_used_category(used_topics, categories, window=30):
    from collections import Counter
    counts = Counter()
    for t in used_topics[-window:]:
        slug = slugify(t)
        for c in categories:
            cw = c.replace("-", " ")
            if cw in t.lower() or c in slug:
                counts[c] += 1
                break
    sorted_cats = sorted(categories, key=lambda c: counts.get(c, 0))
    return random.choice(sorted_cats[:max(5, len(sorted_cats) // 3)])


def _forced_pattern_hint(used_topics, recent_n=5):
    if len(used_topics) < recent_n:
        return None
    prefixes = [_pattern_of(t) for t in used_topics[-recent_n:]]
    most_common = max(set(prefixes), key=prefixes.count)
    if prefixes.count(most_common) >= 4:
        candidates = [p for p in PATTERN_PREFIXES if p != most_common]
        return random.choice(candidates)
    return None


# v12: 제목 클리셰 가드 — 사이트가 스스로 금지한 양산 단어가 제목으로 새던 구멍
_TITLE_CLICHES = ("unlock", "discover", "boost", "maximize", "secrets", "ultimate guide",
                  "essential guide", "game-changer", "revolutioniz")


def generate_unique_topic(used_topics, existing_slugs, max_attempts=7):
    """v8: GPT가 단일 니치(HYSA/CD/MMA) 안에서 설명형/비교형 고유 토픽 생성.
    카테고리 회전 + 패턴 회전 + 키워드 차단 + 의미 유사도 차단. 날조형 패턴 제거.
    """
    client = OpenAI()
    year = datetime.datetime.now().year
    used_set = set(slugify(t) for t in used_topics[-200:]) | existing_slugs
    used_list = "\n".join(f"- {t}" for t in used_topics[-30:]) if used_topics else "(none yet)"

    banned_keywords = _recent_keywords(used_topics, window=7, top_n=4)
    banned_str = ", ".join(banned_keywords) if banned_keywords else "(none yet)"
    forced_pattern = _forced_pattern_hint(used_topics, recent_n=5)

    title = ""
    slug = ""
    category = random.choice(CATEGORIES)
    last_reason = ""
    for attempt in range(max_attempts):
        category = _least_used_category(used_topics, CATEGORIES, window=30)
        temperature = 1.0 + 0.1 * attempt

        hints = []
        if forced_pattern:
            hints.append(f"FORCED PATTERN: title MUST start with '{forced_pattern.title()}' (recent 5 posts overused other patterns).")
        if attempt > 0:
            hints.append(f"PREVIOUS attempt #{attempt} rejected ({last_reason}). Try a totally different angle, topic, AND pattern.")

        forced_hint = ("\n" + "\n".join(hints)) if hints else ""

        response = _openai_retry(lambda: client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=400,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You generate blog post titles for a blog focused narrowly on {BLOG_NICHE} in the United States.\n"
                        "Generate clear, informational titles that match what people actually search when researching "
                        "savings accounts, CDs, and money market accounts.\n\n"
                        "Use a MIX of these explainer / comparison patterns (do NOT default to one):\n"
                        "1. 'How does a [thing] work?'\n"
                        "2. 'What is [thing] and how is it calculated?' (e.g., APY, FDIC coverage, compounding)\n"
                        "3. '[Thing A] vs [Thing B]: which fits [situation]?' (e.g., HYSA vs money market account)\n"
                        "4. 'How to compare [thing] without getting burned'\n"
                        "5. 'Is a [thing] worth it right now?'\n"
                        "6. 'Common mistakes with [thing] (and how to avoid them)'\n"
                        "7. 'How [thing] is taxed' or 'What happens to [thing] when interest rates change'\n"
                        "8. 'A beginner's guide to [thing]'\n\n"
                        "Rules:\n"
                        "- Real, natural Google search phrasing (5-12 words).\n"
                        "- Informational / decision intent — NOT fake 'I tried it for 30 days' angles.\n"
                        "- Do NOT promise a specific current rate or dollar result in the title.\n"
                        f"- Relevant to {year}, but do NOT bake a year number into most titles.\n"
                        "- MUST be clearly different in topic AND angle from the used titles below.\n"
                        "- Do NOT merely synonym-swap an existing title.\n"
                        f"- BANNED keywords (over-represented recently, do not use any of these): {banned_str}.\n"
                        f"{forced_hint}\n\n"
                        "Reply with ONLY the title, nothing else."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Category: {category.replace('-', ' ')}\n\n"
                        f"Already used titles (DO NOT repeat or rephrase these):\n{used_list}\n\n"
                        "Generate one new unique title:"
                    ),
                },
            ],
        ))
        title = response.choices[0].message.content.strip().strip('"').strip("'")
        slug = slugify(title)
        norm_slug = re.sub(r"-\d{2,3}$", "", slug)

        if norm_slug in used_set:
            last_reason = "duplicate slug"
            continue

        title_lower = title.lower()
        hit_banned = [bk for bk in banned_keywords if bk in title_lower]
        if hit_banned:
            last_reason = f"banned keyword used: {hit_banned[0]}"
            continue

        # v12: 제목에도 AI 클리셰 가드 (메타에만 있던 검사를 제목까지 — 'Unlocking...' 통과 사고 재발 방지)
        hit_cliche = [c for c in _TITLE_CLICHES if c in title_lower]
        if hit_cliche:
            last_reason = f"cliche word in title: {hit_cliche[0]}"
            continue

        new_words = _title_words(title)
        worst_jaccard = 0.0
        # v12: 최근 30개 → 전체 이력 검사 (21일 지나면 같은 글이 다시 나오던 준중복 구멍 봉합)
        for past in used_topics:
            j = _jaccard(new_words, _title_words(past))
            if j > worst_jaccard:
                worst_jaccard = j
        if worst_jaccard >= 0.5:
            last_reason = f"too similar (jaccard {worst_jaccard:.2f})"
            continue

        return title, category, slug

    # v12: fail-closed — 시도 소진 시 유사/중복 제목을 그대로 발행하던 fail-open 제거.
    # __main__ 의 per-post try/except 가 잡아 이 회차 발행만 건너뛴다.
    raise RuntimeError(f"unique topic generation failed after {max_attempts} attempts (last: {last_reason})")


def generate_post_content(title, category, recent_titles, min_words=1500):
    """Generate accurate, useful blog post with FAQ and internal linking. (retry 3x)"""
    client = OpenAI()
    return _generate_post_content_inner(client, title, category, recent_titles, min_words)


# === v8 word count (2026-05-23) — quality over padding =============
def _enforce_word_count(client, title, content, min_words=1500, max_extra_words=600):
    """본문이 min_words 미만이면 1회만 가볍게 보강. 무리한 확장(thin/padding 신호) 금지.
    날조 금지 — 지어낸 수치/날짜/개인경험 추가 금지."""
    wc = len(content.split())
    if wc >= min_words:
        return content
    try:
        resp = _openai_retry(lambda: client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2500,
            messages=[
                {"role": "system", "content": (
                    "You add ONE genuinely useful, accurate section to a US personal-finance explainer about "
                    "savings accounts, CDs, or money market accounts. "
                    "Do NOT invent dollar amounts, dates, current APYs, or personal results. "
                    "Add a section that explains a mechanism or comparison the reader actually needs. "
                    "NO filler, NO repetition. Return ONLY the new section (start directly with '## ')."
                )},
                {"role": "user", "content": (
                    f"My post titled \"{title}\" is currently {wc} words; I'd like it a bit more complete "
                    f"(around {min_words} words) WITHOUT padding or fabrication.\n"
                    f"Add ONE accurate H2 section that genuinely fits the topic.\n\n"
                    f"Existing post (do not repeat content from this):\n---\n{content[:6000]}\n---"
                )},
            ],
        ))
        extra = resp.choices[0].message.content.strip()
        # v12: 글 '맨 끝' append 금지 — 결론 뒤에 고아 섹션이 붙는 조립 흔적(76/107편 실측)의 원인이었다.
        # 결론 문단이 있으면 그 앞에, 없으면 마지막 H2 섹션 앞에 삽입.
        pos = content.rfind("\nIn conclusion")
        if pos == -1:
            h2s = list(re.finditer(r"\n##\s", content))
            pos = h2s[-1].start() if len(h2s) >= 2 else -1
        if pos != -1:
            return content[:pos].rstrip() + "\n\n" + extra + "\n\n" + content[pos:].lstrip("\n")
        return content.rstrip() + "\n\n" + extra
    except Exception as _e:
        print(f"[expand] failed: {_e}")
        return content


# === v12 (2026-07-13) — 글별 구조 로테이션: 고정 8단 골격(전 글 동일 = 양산 지문) 제거 =====
_QUICK_LABELS = ["Quick answer", "Bottom line", "In short", "The short version"]
_MISTAKE_HEADINGS = ["Common Mistakes", "What People Get Wrong", "Pitfalls to Avoid", "Mistakes to Avoid"]
_FAQ_HEADINGS = ["Frequently Asked Questions", "FAQ", "Common Questions", "Questions Savers Ask"]


def _build_structure_plan():
    """글마다 다른 골격을 확률적으로 조립. 반환된 플랜 텍스트가 user 프롬프트에 그대로 들어간다."""
    parts = []
    if random.random() < 0.5:
        label = random.choice(_QUICK_LABELS)
        parts.append(
            f'- Open with ONE blockquote: "> **{label}:** <40-60 words: accurate direct answer to the title, '
            'with one general (non-fabricated) number or rule>." Then a blank line, then a 1-2 sentence specific lead.'
        )
    else:
        parts.append(
            "- NO opening blockquote. Open directly with a specific 2-3 sentence lead "
            "(a common mistake, a true general fact, or the core question) — no generic intro."
        )
    h2_count = random.randint(4, 8)
    q_share = random.choice(["one or two", "roughly half", "most"])
    parts.append(
        f"- {h2_count} H2 sections total; {q_share} of them phrased as real search questions, each followed "
        "immediately by a direct 40-60 word answer before expanding. The rest use plain descriptive headings."
    )
    if random.random() < 0.65:
        parts.append("- Include ONE Markdown comparison table (4+ rows, 3-4 columns) of stable, real attributes.")
    if random.random() < 0.45:
        parts.append(
            "- Include a practical checklist section readers can follow in order — write your own natural "
            "heading for it (do NOT title it 'How to Compare X Yourself')."
        )
    if random.random() < 0.5:
        parts.append(
            f"- Include a '## {random.choice(_MISTAKE_HEADINGS)}' section: 3 accurate misconceptions, "
            "each with a one-line 'Why it matters:' explanation."
        )
    if random.random() < 0.45:
        parts.append(
            "- Include ONE fully worked, clearly hypothetical numeric example (labeled 'for example, if you had...'), "
            "walking through the arithmetic step by step."
        )
    if random.random() < 0.55:
        parts.append(f"- Near the end, include '## {random.choice(_FAQ_HEADINGS)}' with 3-5 ### Q&A pairs, accurate and specific.")
    parts.append(
        "- Close with a short conclusion and one concrete next step the reader can take today. "
        "Vary the closing style — do NOT open the final paragraph with 'In conclusion'."
    )
    return "\n".join(parts)


def _generate_post_content_inner(client, title, category, recent_titles, min_words=1500):
    _year = datetime.datetime.now().year

    internal_links_hint = ""
    if recent_titles:
        links = "\n".join(f"- {t}" for t in recent_titles[:10])
        internal_links_hint = (
            "\n\nINTERNAL LINKING (mandatory, SEO-critical):\n"
            "- Reference AT LEAST 3 of the related articles below inside the body text.\n"
            "- Mention each one by its EXACT title in double quotes — NEVER in [square brackets] "
            "(bare brackets render as broken markup).\n"
            "- Weave them into natural, impersonal sentences (e.g., 'see \"Exact Title\"', "
            "'our guide \"Exact Title\" walks through this'). Do NOT write 'as I covered in' — the site "
            "discloses AI-assisted drafting, so first-person authorship claims are off. "
            "Do not invent URLs — the titles alone are enough; a post-processor will link them.\n"
            "- Spread them across different sections of the article.\n\n"
            f"Related articles to reference (exact titles):\n{links}"
        )

    user_content = (
        f'Write an accurate, genuinely useful article titled: "{title}"\n\n'
        f"Category: {category.replace('-', ' ')}\n"
        f"Topic scope: {BLOG_NICHE} (United States).\n\n"
        f"LENGTH: roughly {min_words}-{min_words + 500} words. Quality and accuracy beat length. Do NOT pad. "
        "If you run short, add another genuinely useful angle — never filler.\n\n"
        "ACCURACY (most important — this is what gets the site approved):\n"
        "- Do NOT invent dollar amounts, dates, personal results, or specific CURRENT APYs.\n"
        "- Use ranges / typical behavior, named public references (FDIC $250,000 coverage per depositor per bank per "
        "ownership category, FDIC national-average rates, Federal Reserve rate decisions, NCUA for credit unions), "
        "and clearly-labeled hypotheticals ('for example, if you had $10,000 at 4% APY...').\n"
        f"- Everything must be consistent with the year {_year}. Do NOT cite a past personal result with a specific date.\n\n"
        "STRUCTURE PLAN for THIS article (follow exactly — other articles on the site use different plans):\n"
        f"{_build_structure_plan()}\n"
        "Do NOT add an 'About the Author' section — author info is rendered by the site layout.\n\n"
        "SOURCES: reference real authorities by name (FDIC, Federal Reserve, CFPB, NCUA, U.S. Treasury) and what they "
        "actually provide. Do NOT fabricate URLs, study titles, or statistics.\n\n"
        "BANNED phrases (instant AI flag): 'In today's fast-paced world', 'In the modern era', 'Have you ever wondered', "
        "'Welcome to my blog', 'Let's dive in', 'delve into', 'unlock the secrets', 'embark on a journey', "
        "'in the realm of', 'tapestry of', 'ever-evolving landscape', 'navigate the world of', 'treasure trove'.\n"
        "Do NOT fabricate a personal anecdote with a specific past date or dollar amount.\n\n"
        "FINAL SELF-CHECK (do silently, then output the article):\n"
        "  - Any invented specific current APY, dollar result, or dated personal story? Remove or replace it.\n"
        "  - Does the article follow the STRUCTURE PLAN above (and nothing from a different fixed skeleton)?\n"
        "  - No 'About the Author' section in the body?\n"
        "  - Zero banned phrases, zero fabrication?\n"
        "If any check fails, fix it before output."
        f"{internal_links_hint}"
    )

    response = _openai_retry(lambda: client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=8000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.replace("{YEAR}", str(_year))},
            {"role": "user", "content": user_content},
        ],
    ))

    content = response.choices[0].message.content
    content = _enforce_word_count(client, title, content, min_words=min_words)
    return content


# 메타 디스크립션 양산 템플릿 단어 — 검출되면 재생성 (GPT가 프롬프트만으론 가끔 어김)
_BANNED_META = (
    "unlock", "discover", "boost", "maximize", "don't miss out", "dont miss out",
    "explore", "dive into", "learn everything", "in this guide", "find out how",
    "in our comprehensive guide", "the secrets",
)


def generate_meta_description(title):
    """v9 (2026-05-26): CTR 메타 + 양산 템플릿 단어 후처리 차단(최대 3회 재생성)."""
    client = OpenAI()
    sys_msg = (
        "Write a meta description for a blog post that ranks on Google. "
        "RULES: "
        "1) Length: 145-155 characters (Google truncates at ~155). "
        "2) Main keyword from the title MUST appear in the FIRST 60 characters. "
        "3) Do NOT promise a specific current interest rate (rates change). "
        "4) Write a natural, specific summary of THIS post's actual angle — not a reusable template. "
        "VARY THE OPENING every time: rotate between a real question (How/Why/What/When), a plain "
        "statement, or a concrete point. Do NOT always start with a command verb or a '5 ways / 7 tips' count. "
        "Use a numeric count ONLY if it is a real, stable fact (e.g. $250k FDIC), never a forced 'N ways/tips/steps'. "
        "BANNED words/phrases (instant AI-template flag — never use any of these): 'Unlock', 'Discover', "
        "'Boost', 'Maximize', \"Don't miss out\", 'Explore', 'Dive into', 'Learn everything', "
        "'In this guide', 'Find out how', 'In our comprehensive guide', 'the secrets'. "
        "Reply with ONLY the description, no quotes, no leading 'Meta:'."
    )
    desc = ""
    for attempt in range(3):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=120,
            temperature=0.7 + 0.15 * attempt,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": (
                    f"Blog post title: {title}. Write the meta description now."
                    + ("" if attempt == 0 else " Your previous attempt used a banned template word — rewrite WITHOUT any banned word.")
                )},
            ],
        )
        desc = response.choices[0].message.content.strip().strip('"').strip("'")
        low = desc.replace("’", "'").lower()
        if not any(b in low for b in _BANNED_META):
            break
    else:
        # v11 (2026-06-10): 3회 재생성 후에도 BANNED 잔존 시 결정적 동의어 치환 (누수 0 보장)
        _despam = {"unlock": "understand", "discover": "see", "boost": "grow",
                   "maximize": "make the most of", "explore": "compare", "dive into": "review",
                   "don't miss out": "", "dont miss out": "", "learn everything": "learn what matters",
                   "in this guide": "here", "find out how": "see how",
                   "in our comprehensive guide": "here", "the secrets": "the details"}
        for bad, good in _despam.items():
            desc = re.sub(re.escape(bad), good, desc.replace("’", "'"), flags=re.IGNORECASE)
        desc = re.sub(r"\s{2,}", " ", desc).strip(" .,") + "."
        # 치환으로 첫 글자가 소문자가 되면 대문자화
        if desc and desc[0].islower():
            desc = desc[0].upper() + desc[1:]
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0] + "..."
    return desc[:160]


# === v12 (2026-07-13) — 1차출처 실링크: '인용한다' 주장만 있고 외부 링크 0이던 모순 해소 ======
# 실존 확인(2026-07-13 curl 200)된 공식 URL만. GPT가 URL을 만들지 않도록 후처리에서만 링크.
_SOURCE_LINKS = [
    (r"FDIC's BankFind( Suite)?|BankFind( Suite)?", "https://banks.data.fdic.gov/bankfind-suite/bankfind"),
    (r"FDIC", "https://www.fdic.gov/resources/deposit-insurance"),
    (r"Federal Reserve", "https://www.federalreserve.gov/monetarypolicy.htm"),
    (r"Consumer Financial Protection Bureau|CFPB", "https://www.consumerfinance.gov/"),
    (r"National Credit Union Administration|NCUA", "https://ncua.gov/consumers/share-insurance-coverage"),
    (r"U\.S\. Treasury", "https://www.treasurydirect.gov/"),
]

_MD_LINK_SPLIT = re.compile(r"(\[[^\]]*\]\([^)]*\)|!\[[^\]]*\]\([^)]*\))")


def _link_primary_sources(content, max_links=3):
    """본문에서 1차출처 기관명 첫 언급을 공식 URL로 링크 (헤딩/기존 링크/이미지 제외)."""
    lines = content.split("\n")
    linked = 0
    used_urls = set()
    for pattern, url in _SOURCE_LINKS:
        if linked >= max_links or url in used_urls:
            continue
        rx = re.compile(r"\b(" + pattern + r")\b")
        done = False
        for i, line in enumerate(lines):
            if done:
                break
            if line.lstrip().startswith("#") or line.lstrip().startswith("|"):
                continue  # 헤딩·표는 링크 안 넣음
            segments = _MD_LINK_SPLIT.split(line)
            for j, seg in enumerate(segments):
                if j % 2 == 1:  # 이미 마크다운 링크/이미지인 조각
                    continue
                m = rx.search(seg)
                if m:
                    segments[j] = seg[:m.start()] + f"[{m.group(1)}]({url})" + seg[m.end():]
                    lines[i] = "".join(segments)
                    linked += 1
                    used_urls.add(url)
                    done = True
                    break
    return "\n".join(lines)


_BARE_BRACKET = re.compile(r"\[([^\[\]\n]{10,120})\](?!\()")


def _resolve_bare_brackets(content, recent_posts):
    """v12b: GPT가 남긴 생 대괄호 [Title] 참조를 발행 전에 해소 — 실존 제목이면 실링크, 아니면 대괄호 제거."""
    title_map = {re.sub(r"\s+", " ", p["title"].replace("’", "'").strip().strip(".").lower()): p["url"]
                 for p in recent_posts if p.get("title") and p.get("url")}

    def repl(m):
        t = m.group(1)
        key = re.sub(r"\s+", " ", t.replace("’", "'").strip().strip(".").lower())
        if key in title_map:
            return f"[{t}]({title_map[key]})"
        if t[0].isupper() and len(t.split()) >= 3:
            return t  # 제목처럼 보이지만 매칭 없음 → 대괄호만 벗겨 깨진 마크업 방지
        return m.group(0)

    return _BARE_BRACKET.sub(repl, content)


def create_post():
    """Generate and save a new unique blog post."""
    used_topics = load_used_topics()
    existing_slugs = get_existing_slugs()
    recent_posts = get_recent_posts_for_linking(10)
    recent_titles = [p["title"] for p in recent_posts]

    title, category, slug = generate_unique_topic(used_topics, existing_slugs)
    print(f"Generating post: {title}")
    print(f"Category: {category}")

    # v12: 단어수 밴드 확대 — 균질한 1300~1900 협대역(양산 신호) 대신 자연 분산
    _band = random.random()
    if _band < 0.2:
        _min_words = random.randint(700, 1000)
    elif _band < 0.85:
        _min_words = random.randint(1200, 1800)
    else:
        _min_words = random.randint(1900, 2300)

    content = generate_post_content(title, category, recent_titles, min_words=_min_words)
    content = inject_internal_links(content, recent_posts, min_links=5, max_links=8)
    content = _resolve_bare_brackets(content, recent_posts)
    # v11 (2026-06-10): 본문 About the Author 섹션 제거 — 모든 글에 동일 고정 단락 반복은 양산 시그니처
    # (codex 지적). 저자 표기는 _layouts/post.html author-box 하나로 단일화.
    content = re.sub(r"\n*^##\s+About the Author\b.*?(?=\n##\s|\Z)", "", content,
                     flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
    # v12: 'Last reviewed ... by Kkuma Park' 자동 날인 제거 — 실제 검수 없이 봇이 찍는 가짜
    # 검수 스탬프는 정직성 결격(발행일은 레이아웃이 이미 표시). 실검수한 글만 수동 표기.
    content = _link_primary_sources(content)
    description = generate_meta_description(title)

    # v7 (2026-05-08): 자동 핀 이미지 생성 + 본문 맨 위 markdown 이미지 삽입
    try:
        from generate_blog_pin import generate_pin as _gen_pin
        _today = datetime.datetime.now()
        _date_str = _today.strftime("%Y-%m-%d")
        _pin_dir = os.path.join(get_repo_root(), "assets", "pin-images")
        os.makedirs(_pin_dir, exist_ok=True)
        _pin_filename = f"{_date_str}-{slug}.png"
        _pin_path = os.path.join(_pin_dir, _pin_filename)
        _gen_pin(title, BLOG_NAME, category, _pin_path)
        _pin_url = f"/{BLOG_NAME}/assets/pin-images/{_pin_filename}"
        content = f"![{title}]({_pin_url})\n\n" + content
        print(f"  pin image: {_pin_path}")
    except Exception as _e:
        print(f"  [pin] failed (non-fatal): {_e}")

    today = datetime.datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    posts_dir = os.path.join(get_repo_root(), "_posts")
    os.makedirs(posts_dir, exist_ok=True)

    # v12: 태그 고정 3종([category, niche, 연도]) → 가변 — '태그 정확히 3개+2026 리터럴 107/107' 지문 제거
    _tag_pool = ["savings", "banking", "deposit-accounts", "interest-rates-explained", "personal-finance"]
    _tags = [category] + random.sample(_tag_pool, k=random.randint(1, 3))
    _tags_str = ", ".join(dict.fromkeys(_tags))  # 순서 보존 중복 제거

    # 파일명 충돌 방지 — 같은 날 같은 slug 면 -2, -3, ... 자동 접미사
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(posts_dir, filename)
    suffix = 2
    while os.path.exists(filepath):
        filename = f"{date_str}-{slug}-{suffix}.md"
        filepath = os.path.join(posts_dir, filename)
        suffix += 1
        if suffix > 99: break  # 안전장치

    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category}]
description: "{description}"
tags: [{_tags_str}]
---

{content}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    # Track used topic
    used_topics.append(title)
    save_used_topics(used_topics)

    print(f"Post saved: {filepath}")
    return filepath, filename


if __name__ == "__main__":
    from promo_post import should_write_promo, create_promo_post

    # POST_COUNT 환경변수로 한 번 실행에 여러 글 배치 생성 (기본 1). 개별 실패는 건너뛰고 계속.
    count = max(1, int(os.environ.get("POST_COUNT", "1") or "1"))
    ok = 0
    for i in range(count):
        try:
            if should_write_promo():
                print(f"[{i+1}/{count}] Generating promotional post...")
                filepath, filename = create_promo_post()
            else:
                filepath, filename = create_post()
            ok += 1
            print(f"[{i+1}/{count}] Done: {filename}")
        except Exception as _e:
            print(f"[{i+1}/{count}] FAILED (skipped): {_e}")
    print(f"All done. {ok}/{count} posts generated.")


# v4_wordcount_patched
# v5_diversity_patched 2026-05-06
# v6_seo_patched 2026-05-08
# v7_pin_patched 2026-05-08
# v8_accuracy_rebuild 2026-05-23  (single niche HYSA/CD/MMA, no fabrication, 1st-party sources)
