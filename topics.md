---
layout: default
title: "Browse by Topic"
permalink: /topics/
description: "All SmartMoneyDaily guides grouped by topic: high-yield savings, CDs, money market accounts, FDIC insurance, and more."
---

# Browse by Topic

## Calculators

Ten browser-based tools for the arithmetic behind these decisions — comparing two offers, pricing a CD
penalty, checking insurance coverage, and seeing what a yield is worth after fees, tax, and inflation.

<ul>
  {% for t in site.data.tools %}
  <li><a href="{{ t.url | relative_url }}">{{ t.title }}</a> — {{ t.blurb }}</li>
  {% endfor %}
</ul>

<p><a href="{{ '/tools/' | relative_url }}">What all of them assume, and where the inputs come from</a></p>

{% assign cats = "high-yield-savings|cd-rates|money-market|fdic-insurance|savings-strategy|bank-comparison|interest-rates|emergency-fund" | split: "|" %}
{% for cat in cats %}
{% assign posts = site.categories[cat] %}
{% if posts and posts.size > 0 %}
## {{ cat | replace: "-", " " | capitalize }}

<ul>
  {% for post in posts %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <span style="color:#94a3b8; font-size:0.85em;">{{ post.date | date: "%b %Y" }}</span></li>
  {% endfor %}
</ul>
{% endif %}
{% endfor %}
