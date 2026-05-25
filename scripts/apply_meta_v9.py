# -*- coding: utf-8 -*-
"""Claude가 직접 작성한 메타 디스크립션을 기존 글에 적용 (OpenAI API 미사용).
slug(파일명 날짜 제외) → 메타. frontmatter description 한 줄만 교체."""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "_posts")

META = {
"how-to-maximize-your-interest-earnings-with-certificate-laddering-strategies":
    "Certificate laddering spreads savings across CDs with staggered maturities, balancing higher rates with regular access. Here's how to build one for your goals.",
"how-to-choose-the-right-money-market-account-for-your-needs":
    "Choosing a money market account comes down to rate, fees, minimums, and access. Compare them carefully to match one to the way you actually save.",
"how-to-calculate-the-apy-for-high-yield-savings-accounts":
    "APY shows what a high-yield savings account truly earns once compounding counts. Learn how to calculate it and compare accounts on equal footing.",
"what-happens-when-you-cash-out-a-cd-early":
    "Cashing out a CD before maturity usually triggers an early-withdrawal penalty. Here's what it costs, when it's still worth it, and how to plan around the rules.",
"common-misconceptions-about-money-market-accounts-and-their-benefits":
    "Money market accounts are easily confused with money market funds and checking. Learn what they really are, how FDIC coverage applies, and where they fit.",
"what-are-the-benefits-of-opening-a-cd-in-2026":
    "A CD locks in a fixed rate for a set term, which can help when rates may fall. Here's what opening one offers and who gains most from the trade-off.",
"understanding-fdic-insurance-what-you-need-to-know-before-opening-an-account":
    "FDIC insurance covers up to $250,000 per depositor, per bank, per ownership category. Here's what it protects and how to confirm your bank qualifies.",
"how-to-navigate-fluctuating-interest-rates-on-savings-options":
    "When the Federal Reserve moves rates, savings yields tend to follow, though timing varies. Learn how to keep your money working as rates rise and fall.",
"hysa-vs-cds-which-is-better-for-your-savings-goals":
    "HYSAs stay liquid with variable rates; CDs lock a fixed rate for a term. Here's how the two compare so you can match each to the right savings goal.",
"is-a-money-market-fund-the-right-choice-for-your-emergency-fund":
    "A money market fund isn't FDIC-insured like a savings account, which matters for an emergency fund. Here's how it works and whether it suits cash you need fast.",
"how-to-find-the-best-savings-accounts-for-your-financial-goals":
    "Finding the right savings account means weighing APY, fees, access, and FDIC coverage. Compare HYSAs, CDs, and money market accounts to fit your goals.",
"understanding-high-yield-savings-accounts-key-features-to-consider":
    "High-yield savings accounts pay more than standard ones, but details matter. Check the rates, fees, terms, and FDIC coverage before you open one.",
"how-fdic-insurance-protects-your-savings-accounts-from-loss":
    "FDIC insurance keeps savings safe up to $250,000 even if a bank fails. Here's how the coverage is calculated and how to be sure you're fully protected.",
"what-you-should-know-about-early-withdrawal-penalties-on-cds":
    "Early-withdrawal penalties on CDs can erase months of interest if you break the term. Learn how they're set, how to estimate them, and how to avoid surprises.",
"a-beginners-guide-to-understanding-cd-terms-and-conditions":
    "CD terms like maturity, APY, and early-withdrawal penalty decide what you earn. Here's a plain-English guide to the conditions before you commit your money.",
"what-to-consider-before-opening-a-certificate-of-deposit":
    "Before opening a certificate of deposit, weigh the term, rate, penalty, and your timeline. Here's what to check so the money you lock away truly works for you.",
"emergency-fund-basics-how-much-should-you-really-save":
    "An emergency fund usually means three to six months of essential expenses. Here's how to size yours and where to keep it so it stays safe and reachable.",
"understanding-compounding-interest-on-high-yield-savings-a-comprehensive-guide":
    "Compounding grows high-yield savings faster the more often interest is applied. See how daily versus monthly compounding works and why the frequency matters.",
"how-to-assess-the-value-of-a-cd-in-todays-market":
    "Whether a CD is worth it depends on its term, rate, and your need for access. Here's how to weigh a CD against flexible savings before locking your money in.",
"what-to-know-about-the-impact-of-interest-rate-changes-on-your-earnings":
    "Interest rate changes ripple into what your savings and CDs actually earn. See how rate moves affect deposit yields and what savers can do as they shift.",
"common-mistakes-people-make-with-certificates-of-deposit-and-how-to-avoid-them":
    "Common CD mistakes — ignoring penalties, auto-renewal, or term length — quietly cost savers. Here's what to watch for and how to avoid the priciest ones.",
}

changed = 0
missing = []
for path in sorted(glob.glob(os.path.join(POSTS, "*.md"))):
    fn = os.path.basename(path)
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", fn)
    if not m:
        continue
    slug = m.group(1)
    if slug not in META:
        missing.append(slug)
        continue
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    new_meta = META[slug].replace('"', "'")
    new_txt, n = re.subn(r'(?m)^description:\s*".*"\s*$',
                         'description: "' + new_meta + '"', txt, count=1)
    if n and new_txt != txt:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_txt)
        changed += 1
        print(f"  {slug}: {len(META[slug])} chars")

print(f"\n{changed} metas applied. missing(no meta): {missing}")
print("=== length check (target 140-158) ===")
for s, mt in META.items():
    flag = "" if 130 <= len(mt) <= 160 else "  <-- CHECK"
    print(f"  {len(mt):3d}  {s[:40]}{flag}")
