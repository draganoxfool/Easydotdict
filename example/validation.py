"""
example: validation.py — Type-check API responses with .expect() and @expect_schema
"""

from easydotdict import dotdict, expect_schema

user = dotdict({"name": "Alice", "age": 30, "email": "alice@example.com"})

user.expect({"name": str, "age": int, "email": str})
print("Valid user")

try:
    bad = dotdict({"name": "Bob", "age": "unknown"})
    bad.expect({"name": str, "age": int})
except TypeError as e:
    print(f"Caught: {e}")

@expect_schema({"name": str, "age": int})
def save_user(u):
    print(f"Saving {u.name}, age {u.age}")

save_user(dotdict({"name": "Charlie", "age": 25}))

try:
    save_user(dotdict({"name": 123, "age": 25}))
except TypeError as e:
    print(f"Decorator caught: {e}")
