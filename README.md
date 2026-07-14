# easydotdict

**Navigate nested dictionaries with the simplicity of attribute access.**  
Zero dependencies. Python 3.8+.

```python
from easydotdict import dotdict

d = dotdict({"user": {"profile": {"name": "Alice"}}})

# Read deeply with dot notation
print(d.user.profile.name)   # Alice
print(d["user"].profile.name)  # same, dual access

# Safe missing-key access — no exceptions
print(d.user.email)          # None

# Auto-create nested paths on assignment
d.config.database.host = "localhost"

# Scalar auto-conversion — string becomes a key
d.name = "Alice"
d.name.character = 5  # {"name": {"Alice": {"character": 5}}}

# Deep path string methods
d.put("server.port", 8080)
print(d.dig("user.name"))    # Alice

# Compare, diff, and migrate
v1 = dotdict({"app": {"debug": True}})
v2 = dotdict({"app": {"debug": False, "version": "2.0"}})
changes = v1.diff(v2)
v1.patch(changes)            # v1 now matches v2

# Recursive flatten and restore
flat = d.flatten()
restored = dotdict.unflatten(flat)

# Deep merge with key preservation
d.merge({"settings": {"theme": "dark"}})

# Pretty-printed JSON output
print(d)
```

## Features

| Category | Capabilities |
|---|---|
| **Access** | Dot notation (`d.user.name`), bracket notation (`d["user"]`), dual interchangeability |
| **Safety** | Missing keys return `None` — no `KeyError` or `AttributeError` |
| **Auto-vivification** | `d.a.b.c = value` creates intermediate structures automatically |
| **Scalar conversion** | `d.name = "Alice"; d.name.x = 1` promotes scalars to nested dicts |
| **Deep paths** | `dig()`, `get()`, `put()`, `has()` with dot-separated strings; handles list indices (`users.0.name`) |
| **Flatten / Unflatten** | Recursive flatten to dot-keys and restoration via `unflatten()` |
| **Deep merge** | `update()` and `merge()` merge recursively, preserving existing keys |
| **Diff & Patch** | `diff(other)` produces `{path: {"from": ..., "to": ...}}`; `patch()` applies changes |
| **Batch operations** | `set_many({path: value})` and `delete(*paths)` for bulk mutations |
| **Search** | `find(name)` locates all dot-paths matching a key name anywhere in the tree |
| **Cursor** | Lightweight views into nested paths — mutations affect the original |
| **Type validation** | `expect(schema)` validates types at runtime; `@expect_schema` for functions |
| **Change tracking** | `on_change(path, cb)` fires callbacks on mutation |
| **Freeze** | `freeze()` / `unfreeze()` enforces immutability; `@freeze` for return values |
| **Decorators** | `@dotdictify` converts arguments, `@defaults` supplies fallbacks |
| **Comparisons** | Scalars support `<`, `>`, `<=`, `>=` and f-string formatting |
| **Serialisation** | `to_dict()` unwraps to plain `dict` / `list`; pretty-printed JSON via `print()` |
| **Compatibility** | Full `dict` subclass — `keys()`, `items()`, `pop()`, `len()`, `in`, etc. all work |

## Install

```bash
pip install easydotdict
```

## Documentation

Full API reference, edge case table, and decorator guide: [docs.md](docs.md)

Real-world examples:

- [`api_response.py`](example/api_response.py) — consume a JSON API endpoint
- [`app_config.py`](example/app_config.py) — load, edit, and persist application configuration
- [`product_catalog.py`](example/product_catalog.py) — enrich GitHub repository data
- [`config_manager.py`](example/config_manager.py) — validate, watch, freeze, and bulk-override settings
- [`data_migration.py`](example/data_migration.py) — diff, patch, find, and validate between data versions
- [`github_stars.py`](example/github_stars.py) — analyse repository metadata with find, diff, cursor, and expect

## License

MIT
