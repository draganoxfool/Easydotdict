# easydotdict

Make nested dictionaries effortless — dot-notation access, safe missing-key handling, auto-vivification, deep path operations, and pretty-printing. Pure Python, no dependencies.

```python
from easydotdict import dotdict

d = dotdict({'user': {'profile': {'name': 'Alice'}}})
print(d.user.profile.name)       # Alice
print(d['user'].profile.name)    # same
print(d.user.email)              # None (safe, no error)

d.name = 'Alice'
d.name.character = 5  # auto-converts scalar -> nested: {'Alice': {'character': 5}}

d.config.database.host = 'localhost'  # auto-creates path
d.put('server.port', 8080)            # or use path string
print(d.dig('user.name'))             # Alice (deep path getter)

flat = d.flatten()                    # {'user.profile.name': 'Alice', ...}
restored = dotdict.unflatten(flat)   # reverse

d.merge({'settings': {'debug': True}})  # deep merge
print(d)                                # indented JSON
```

## Features

- **Dot notation** — `d.user.profile.name` instead of `d['user']['profile']['name']`
- **Dual access** — dot and bracket notation work interchangeably
- **Safe access** — `d.missing` returns `None`, no `KeyError`/`AttributeError`
- **Auto-vivification** — `d.a.b.c = value` auto-creates intermediate structures
- **Scalar auto-conversion** — `d.name = 'Alice'; d.name.character = 5` wraps scalar into `{'Alice': {'character': 5}}`
- **Deep path operations** — `dig`, `put`, `has`, `get` with dot-separated strings
- **Cursors** — lightweight views into nested paths that mutate the original via `cursor(path)`
- **Diff & Patch** — compare two dotdicts with `diff()`, apply changes with `patch()`
- **Batch operations** — `set_many({path: value})` and `delete(*paths)` for bulk work
- **Search** — `find(name)` returns all dot-paths matching a key name
- **Type validation** — `expect(schema)` validates types at runtime
- **Change tracking** — `on_change(path, cb)` fires callbacks on mutation
- **Freeze** — `freeze()` / `unfreeze()` prevents further modification
- **Flatten / Unflatten** — recursive flatten and restore with `flatten()` and `unflatten()`
- **Deep merge** — `update()` and `merge()` merge recursively, preserving existing keys
- **Clone** — `clone()` returns a deep independent copy
- **Empty check** — `is_empty()` checks if the dict has no keys
- **Auto-conversion** — nested `dict`s and `list`s containing `dict`s are wrapped automatically
- **Pretty-print** — `print(d)` outputs indented JSON
- **Comparisons** — scalars support `<`, `>`, `<=`, `>=` comparisons
- **f-string ready** — format specs like `{d.name:>10}` delegate to the underlying value
- **`to_dict()`** — recursively converts back to plain `dict`s and `list`s
- **Decorators** — `@dotdictify`, `@defaults`, `@expect_schema`, `@freeze` 
- **Pure Python** — standard library only, Python 3.8+

## Install

```bash
pip install easydotdict
```

## Documentation

See [docs.md](docs.md) for full API reference, edge cases, and examples.

## License

MIT
