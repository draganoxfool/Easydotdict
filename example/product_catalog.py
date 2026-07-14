"""
example: product_catalog.py — Fetch GitHub repos as a catalog and enrich with dotdict
Uses:    GitHub API (https://api.github.com, free, no key needed for public data)
"""

from urllib.request import urlopen
from json import loads
from easydotdict import dotdict

url = "https://api.github.com/orgs/python/repos?per_page=5&sort=stars"

with urlopen(url) as r:
    data = loads(r.read())

repos = [dotdict(r) for r in data]

for r in repos:
    print(f"{r.name:25s}  stars: {r.stargazers_count:<5d}  {r.language or 'N/A':10s}")

print()

for r in repos:
    if r.stargazers_count > 1000:
        r.popular = True
        r.tags = ["python", "popular"]

print(repos[0])
