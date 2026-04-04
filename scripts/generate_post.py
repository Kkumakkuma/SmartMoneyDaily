"""
SmartMoneyDaily Auto Post Generator
Generates SEO-optimized personal finance articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for personal finance
TOPIC_POOLS = {
    "credit_score": [
        "How to Improve Your Credit Score Fast in {year}",
        "Credit Score Myths That Are Costing You Money",
        "{number} Ways to Boost Your Credit Score by 100 Points",
        "How Your Credit Score Affects Your Mortgage Rate",
        "Best Credit Cards for Building Credit in {year}",
        "How to Check Your Credit Score for Free",
        "What Is a Good Credit Score and Why It Matters",
    ],
    "saving_money": [
        "How to Save $10,000 in {number} Months on Any Income",
        "{number} Simple Ways to Cut Your Monthly Expenses",
        "The 50/30/20 Budget Rule Explained Simply",
        "How to Build an Emergency Fund from Scratch",
        "Best High-Yield Savings Accounts in {year}",
        "Money-Saving Hacks That Actually Work in {year}",
        "How to Save Money on Groceries Without Coupons",
    ],
    "investing": [
        "Beginner's Guide to Investing in Index Funds",
        "How to Start Investing with Just $100",
        "ETF vs Mutual Fund: Which Is Better for You",
        "How to Build a Diversified Investment Portfolio",
        "{number} Investing Mistakes Beginners Should Avoid",
        "Dollar Cost Averaging: The Simplest Investment Strategy",
        "Roth IRA vs Traditional IRA: Complete Comparison {year}",
    ],
    "debt": [
        "How to Pay Off Credit Card Debt Fast",
        "Debt Snowball vs Debt Avalanche: Which Method Works",
        "How to Get Out of $10,000 in Debt in {number} Months",
        "Should You Consolidate Your Student Loans in {year}",
        "Balance Transfer Cards: How to Use Them to Eliminate Debt",
        "{number} Steps to Becoming Completely Debt-Free",
        "How to Negotiate Lower Interest Rates on Your Debt",
    ],
    "passive_income": [
        "{number} Passive Income Ideas That Actually Work in {year}",
        "How to Make Money While You Sleep",
        "Dividend Investing for Beginners: Complete Guide",
        "How to Build Multiple Streams of Income",
        "Best Side Hustles That Can Replace Your 9-to-5",
        "How to Earn Passive Income with $1,000",
        "Real Estate Investing for Beginners Without Buying Property",
    ],
    "retirement": [
        "How Much Money Do You Need to Retire Comfortably",
        "401(k) Guide: Everything You Need to Know in {year}",
        "How to Retire Early with the FIRE Method",
        "Social Security Benefits: When Should You Start Claiming",
        "Best Retirement Accounts for Self-Employed People",
        "How to Catch Up on Retirement Savings in Your 40s",
        "Retirement Planning Mistakes to Avoid at Every Age",
    ],
    "taxes": [
        "Tax Deductions You Might Be Missing in {year}",
        "How to Reduce Your Tax Bill Legally",
        "Tax Tips for Freelancers and Self-Employed Workers",
        "Understanding Capital Gains Tax: A Simple Guide",
        "Best Tax Software Compared: {year} Edition",
        "How to File Your Taxes for Free in {year}",
        "{number} Year-End Tax Moves to Save You Money",
    ],
    "insurance": [
        "How Much Life Insurance Do You Actually Need",
        "Best Health Insurance Options If You Are Self-Employed",
        "Car Insurance: How to Get the Lowest Rate in {year}",
        "Home Insurance Guide: What Is and Isn't Covered",
        "Term vs Whole Life Insurance: Which One Should You Choose",
        "How to Save Money on Insurance Premiums",
        "Disability Insurance: The Most Overlooked Protection",
    ],
}

SYSTEM_PROMPT = """You are an expert personal finance writer for a blog called SmartMoneyDaily.
Write SEO-optimized, informative, and engaging blog posts.

Rules:
- Write in a friendly, conversational but authoritative tone
- Use short paragraphs (2-3 sentences max)
- Include practical, actionable advice
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are a certified financial planner sharing expertise
- Make content evergreen where possible
- Include specific numbers and examples
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    # In GitHub Actions, the working directory is the repo root
    # Locally, navigate up from scripts/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        # If all attempts hit duplicates, add a random suffix
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Learn practical tips and strategies for your personal finances."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename


if __name__ == '__main__':
    filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
