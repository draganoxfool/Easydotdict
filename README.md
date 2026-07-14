# easydotdict

Make nested dictionaries effortless — dot-notation access, safe missing-key handling, auto-vivification, deep path operations, and pretty-printing. Pure Python, no dependencies.

```python
from easydotdict import dotdict

d = dotdict({'user': {'profile': {'name': 'Alice'}}})
print(d.user.profile.name)       # Alice
print(d['user'].profile.name)    # same
print(d.user.email)              # None (safe, no error)

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
- **Deep path operations** — `dig`, `put`, `has` with dot-separated strings
- **Flatten / Unflatten** — recursive flatten and restore with `flatten()` and `unflatten()`
- **Deep merge** — `update()` and `merge()` merge recursively, preserving existing keys
- **Clone** — `clone()` returns a deep independent copy
- **Empty check** — `is_empty()` checks if the dict has no keys
- **Auto-conversion** — nested `dict`s and `list`s containing `dict`s are wrapped automatically
- **Pretty-print** — `print(d)` outputs indented JSON
- **`to_dict()`** — recursively converts back to plain `dict`s and `list`s
- **Pure Python** — standard library only, Python 3.8+

## Install

```bash
pip install easydotdict
```

## Documentation

See [docs.md](docs.md) for full API reference, edge cases, and examples.

## License

MIT
