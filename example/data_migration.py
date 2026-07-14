"""
example: data_migration.py — Diff two data versions, patch, validate, and clean up
"""

from easydotdict import dotdict

v1 = dotdict({
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@old.com", "role": "admin"},
        {"id": 2, "name": "Bob", "email": "bob@old.com", "role": "user"},
    ],
    "version": "1.0",
})

v2 = dotdict({
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@new.com", "role": "admin", "verified": True},
        {"id": 3, "name": "Charlie", "email": "charlie@new.com", "role": "user"},
    ],
    "version": "2.0",
    "deprecated": True,
})

# diff — See what changed between versions
changes = v1.diff(v2)
print("Changes from v1 to v2:")
for path, ch in sorted(changes.items()):
    print(f"  {path}: {ch['from']} -> {ch['to']}")

# patch — Apply the diff to upgrade v1 to v2
v1.patch(changes)
print(f"\nAfter patch, users count: {len(v1.users)}, version: {v1.version}")

# find — Locate all users who were updated
for p in v1.find('verified'):
    print(f"  Found verified at: {p}")

# delete — Remove deprecated fields
v1.delete('deprecated')
print(f"\nHas 'deprecated' after delete: {v1.has('deprecated')}")

# expect — Validate the migrated structure
v1.expect({"version": str, "users.0.id": int, "users.0.email": str})
print("  Migration validated OK")
