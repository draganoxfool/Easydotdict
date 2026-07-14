"""
example: api_response.py — Fetch live data from an API and work with it
Uses:    JSONPlaceholder (free, no API key needed)
"""

from urllib.request import urlopen
from json import loads
from easydotdict import dotdict

url = "https://jsonplaceholder.typicode.com/users/1"

with urlopen(url) as r:
    data = loads(r.read())

user = dotdict(data)

print(f"Name:    {user.name}")
print(f"Email:   {user.email}")
print(f"City:    {user.address.city}")
print(f"Company: {user.company.name}")

user.phone = "N/A"
user.address.zipcode = "Unknown"

print(f"\nGeo: {user.address.geo.lat}, {user.address.geo.lng}")

print(user)
