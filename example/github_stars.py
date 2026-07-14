"""
example: github_stars.py — Analyze GitHub repos using diff, find, expect, and cursor
Uses:    GitHub API (https://api.github.com, free, no key needed)
"""

from json import loads
from urllib.request import urlopen
from easydotdict import dotdict

url = "https://api.github.com/orgs/python/repos?per_page=5&sort=stars&direction=desc"
with urlopen(url) as r:
    repos = [dotdict(item) for item in loads(r.read())]

# find — What languages do these repos use?
for repo in repos:
    langs = repo.find('language')
    for path in langs:
        val = repo.dig(path)
        if val:
            print(f"  {path}: {val}")

# expect — Validate API response shape for each repo
for repo in repos:
    try:
        repo.expect({"name": str, "stargazers_count": int, "language": (str, type(None))})
    except (KeyError, TypeError) as e:
        print(f"  Invalid repo: {e}")

# diff — Compare two repos
a, b = repos[0], repos[1]
changes = a.diff(b)
print("\nDifferences between top 2 repos:")
for path, ch in sorted(changes.items()):
    if ch['from'] != ch['to']:
        print(f"  {path}: {ch['from']} -> {ch['to']}")

# cursor — Batch-annotate repos
for repo in repos:
    c = repo.cursor('annotations', create=True)
    c.source = 'github'
    c.fetched_at = '2026-07-15'
print(f"\nAnnotated 1st repo: {repos[0].annotations.source}")
