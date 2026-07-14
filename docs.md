# easydotdict Documentation

## Overview

`easydotdict` is a lightweight Python library that wraps dictionaries with dot-notation access, safe missing-key handling, automatic nested conversion, and pretty-printing. No external dependencies.

---

## Installation

```bash
pip install easydotdict
```

Or copy `easydotdict/easydotdict.py` into your project.

---

## Getting Started

```python
from easydotdict import dotdict

d = dotdict({'user': {'profile': {'name': 'Alice'}}})
print(d.user.profile.name)  # Alice
```

---

## Core Features

### Dot & Bracket Notation

Access and set values with either style interchangeably:

```python
d = dotdict()
d.user.name = 'Alice'
d.user['age'] = 30

print(d.user.name)   # Alice
print(d['user'].age) # 30
```

### Safe Missing-Key Access

Dot notation returns `None` for missing keys — no `KeyError` or `AttributeError`:

```python
d = dotdict({'a': 1})
print(d.user.email)  # None (safe, like JS optional chaining)
print(d['b'])        # None
print(d.get('b'))    # None
```

### Auto-Vivification (Chained Assignment)

Create deep nested structures in one statement:

```python
d = dotdict()
d.config.database.host = 'localhost'
d.config.database.port = 5432
# d == {'config': {'database': {'host': 'localhost', 'port': 5432}}}
```

### Scalar Auto-Conversion

Assigning an attribute on a previously scalar value automatically converts it into a nested structure using the original value as the key:

```python
d = dotdict()
d.name = 'Alice'
d.name.character = 5
# d == {'name': {'Alice': {'character': 5}}}
```

This works with any scalar type (strings, ints, floats, bools, None):

```python
d = dotdict()
d.count = 42
d.count.meaning = 'everything'
# d == {'count': {'42': {'meaning': 'everything'}}}
```

Scalar proxies support comparisons (`<`, `>`, `<=`, `>=`) and f-string formatting, delegating to the underlying value:

```python
d = dotdict()
d.count = 42
print(d.count > 10)   # True
print(f"{d.count:05d}")  # 00042
```

### Auto-Conversion

Nested plain `dict`s and `list`s containing `dict`s are automatically wrapped:

```python
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
d = dotdict(data)
print(d.users[0].name)  # Alice
print(type(d.users[0])) # <class 'easydotdict.dotdict'>
```

### Pretty-Printing

`repr()` and `str()` produce indented JSON output:

```python
d = dotdict({'name': 'Alice', 'scores': [90, 95]})
print(d)
# {
#   "name": "Alice",
#   "scores": [
#     90,
#     95
#   ]
# }
```

### Deep Path Operations

Use dot-separated path strings for nested access:

```python
d = dotdict({'user': {'name': 'Alice'}})
print(d.dig('user.name'))       # Alice
print(d.dig('user.missing'))    # None

d.put('server.host', 'localhost')
print(d.server.host)  # localhost

print(d.has('user.name'))   # True
print(d.has('user.email'))  # False
```

### Flatten & Unflatten

Convert nested structures to/from flat dot-separated keys:

```python
d = dotdict({'user': {'name': 'Alice', 'scores': [90, 95]}})
flat = d.flatten()
# flat == {'user.name': 'Alice', 'user.scores.0': 90, 'user.scores.1': 95}

restored = dotdict.unflatten({'a.b.c': 1})
print(restored.a.b.c)  # 1
```

### Deep Merge

Merge another dict recursively, preserving existing keys:

```python
d = dotdict({'user': {'name': 'Alice', 'age': 30}})
d.update({'user': {'email': 'alice@example.com'}})
print(d.user.email)  # alice@example.com
print(d.user.name)   # Alice (preserved)

d.merge({'settings': {'debug': True}})
print(d.settings.debug)  # True
```

### Convert Back to Plain Dict

```python
d = dotdict({'user': {'name': 'Alice'}})
plain = d.to_dict()
# plain == {'user': {'name': 'Alice'}}
# type(plain['user']) == dict
```

---

## API Reference

### `dotdict(*args, **kwargs)`

Creates a new `dotdict`. Accepts the same arguments as `dict()`:

```python
dotdict()                    # empty
dotdict({'a': 1})            # from dict
dotdict(a=1, b=2)            # from keyword args
dotdict([('a', 1), ('b', 2)])  # from iterable
```

---

### Attribute Access

#### `__getattr__(key)`

Dot-notation read. If the key exists, returns the value. If not, returns `None` (via a `_Missing` sentinel proxy). The proxy auto-creates the path if a value is later assigned through it, enabling `d.a.b.c = x` chained assignment.

#### `__setattr__(key, value)`

Dot-notation write. Wraps nested `dict`s and `list`s automatically.

#### `__delattr__(key)`

Dot-notation delete. Raises `AttributeError` if the key does not exist.

---

### Item Access

#### `__getitem__(key)`

Bracket-notation read. Returns `None` for missing keys (safe access).

#### `__setitem__(key, value)`

Bracket-notation write. Wraps nested `dict`s and `list`s automatically.

---

### Conversion

#### `to_dict()`

Recursively converts all nested `dotdict`s back to plain `dict`s and `list`s.

#### `flatten(prefix='')`

Recursively flattens the structure into a flat dict with dot-separated keys. List items use numeric indices (e.g., `items.0.id`).

#### `unflatten(data)` *(class method)*

Reverses `flatten()`. Converts a flat dict with dot-separated keys back into a nested `dotdict`. Numeric keys are converted to lists.

---

### Deep Path Methods

#### `dig(path)`

Traverse a dot-separated path string. Returns the value or `None` if any segment is missing.

#### `put(path, value)`

Traverse a dot-separated path string, creating intermediate `dotdict`s as needed, then set the value.

#### `has(path)`

Returns `True` if the dot-separated path exists, `False` otherwise.

#### `get(path, default=None)`

Supports both single keys and dot-separated deep paths. Returns the value or `default` if any segment is missing. Correctly distinguishes between a key whose value is `None` and a missing key.

```python
d = dotdict({'user': {'name': 'Alice'}})
d.get('user.name')      # 'Alice'
d.get('user.email')     # None
d.get('user.email', 'n/a')  # 'n/a'
```

---

### Mutation

#### `update(other=None, **kwargs)`

Deep merge update. Recursively merges nested dicts, preserving existing keys. Wraps nested `dict`s automatically.

#### `merge(other)`

Deep merge, same as `update()` but returns `self` for chaining.

#### `set_many(items)`

Set multiple values from a flat `{path: value}` dict. Creates intermediate structures as needed:

```python
d = dotdict()
d.set_many({'a.b.c': 1, 'x.y': 2})
# d.a.b.c == 1, d.x.y == 2
```

#### `delete(*paths)`

Delete one or more dot-separated paths. No error if a path doesn't exist:

```python
d = dotdict({'a': {'b': 1, 'c': 2}, 'x': 3})
d.delete('a.b', 'x')
# d == {'a': {'c': 2}}
```

---

### Diff & Patch

#### `diff(other)`

Compare two `dotdict`s and return a flat mapping of changed paths in `{path: {'from': old, 'to': new}}` format. Paths present in one side only use `None` for the missing side:

```python
v1 = dotdict({'app': {'name': 'MyApp', 'debug': True}})
v2 = dotdict({'app': {'name': 'MyApp', 'debug': False, 'version': '2.0'}})
d = v1.diff(v2)
# {
#   'app.debug':     {'from': True,  'to': False},
#   'app.version':   {'from': None,  'to': '2.0'},
# }
```

#### `patch(changes)`

Apply the output of `diff()` (or any `{path: {'to': value}}` dict) directly to the current `dotdict`:

```python
v1.patch(d)
# v1.app.version == '2.0'
```

---

### Cursors

#### `cursor(path, create=False)`

Returns a lightweight view that reads/writes through to the underlying `dotdict` at the given path. Mutations via the cursor affect the original. If `create=True`, intermediate paths are auto-created when setting:

```python
d = dotdict({'db': {'host': 'localhost'}})
c = d.cursor('db')
c.port = 5432
print(d.db.port)  # 5432
```

---

### Search

#### `find(name)`

Search recursively for all keys matching the given name. Returns a sorted list of dot-separated paths to each match:

```python
d = dotdict({'a': {'b': 1, 'c': {'b': 2}}, 'x': {'b': 3}})
d.find('b')
# ['a.b', 'a.c.b', 'x.b']
```

---

### Type Validation

#### `expect(schema)`

Validate types at runtime. Accepts a `{path: type}` schema. Raises `KeyError` if a required path is missing, or `TypeError` if the value doesn't match the expected type:

```python
user = dotdict({'name': 'Alice', 'age': 30})
user.expect({'name': str, 'age': int})  # passes
user.expect({'email': str})             # KeyError: missing
```

---

### Change Tracking

#### `on_change(path, callback)`

Register a callback that fires when a value at the given dot-separated path is set. The callback receives `(path, new_value)`. Only direct assignments trigger the callback:

```python
config = dotdict()
config.app.debug = True

config.on_change('app.debug', lambda p, v: print(f'{p} set to {v}'))
config.app.debug = False  # prints: app.debug set to False
```

---

### Freezing

#### `freeze()`, `unfreeze()`, `is_frozen`

Freeze a `dotdict` to prevent further modifications. Any `__setattr__`, `__setitem__`, `__delattr__`, or `__delitem__` call on a frozen instance raises `AttributeError`:

```python
d = dotdict({'key': 'value'})
d.freeze()
d.key = 'new'     # raises AttributeError
d.new_key = 'x'   # raises AttributeError
del d.key          # raises AttributeError

d.unfreeze()
d.key = 'new'     # works

print(d.is_frozen)  # False
```

---

### Copying & Inspection

#### `copy()`

Returns a deep copy as a new `dotdict`.

#### `clone()`

Explicit deep copy. Returns a new `dotdict` with all nested structures recursively copied.

#### `is_empty()`

Returns `True` if the `dotdict` has no keys.

---

## Decorators

Decorators are available directly from `easydotdict`:

```python
from easydotdict import dotdictify, defaults, expect_schema, freeze
```

#### `@dotdictify`

Wraps a function so that the first positional argument (typically a dict) is automatically converted to a `dotdict`:

```python
@dotdictify
def process(data):
    print(data.user.name)  # data is now a dotdict

process({'user': {'name': 'Alice'}})
```

#### `@defaults(**defaults)`

Apply default values to a `dotdict` before the function body runs:

```python
@defaults(page=1, limit=20)
def list_items(params):
    # params.page defaults to 1, params.limit to 20
    pass

list_items(dotdict())                    # page=1, limit=20
list_items(dotdict({'page': 5}))         # page=5, limit=20
```

#### `@expect_schema(schema)`

Validate the first positional argument at call time using the same schema format as `dotdict.expect()`:

```python
@expect_schema({'name': str, 'age': int})
def save_user(user):
    pass  # only reached if types match

save_user(dotdict({'name': 'Alice', 'age': 30}))  # ok
save_user(dotdict({'name': 123}))                  # TypeError
```

#### `@freeze`

Freezes the return value if it is a `dotdict`, preventing accidental mutation after return:

```python
@freeze
def get_config():
    return dotdict({'debug': True})

cfg = get_config()
# cfg is now frozen — cfg.debug = False would raise AttributeError
```

---

## Inheritance & Compatibility

`dotdict` inherits from `dict`, so all standard dict methods work:

- `keys()`, `values()`, `items()`
- `pop(key, *args)`
- `clear()`
- `len()`, `in`, `iter()`
- `bool()` (empty = `False`)

---

## Edge Cases & Behavior

| Scenario | Behavior |
|----------|----------|
| Access missing key via bracket `d['x']` | Returns `None` |
| Access missing key via dot `d.x` | Returns `None` (via `_Missing` proxy) |
| Set `d.a.b.c = value` with missing intermediates | Auto-creates intermediate `dotdict`s |
| Set attribute on scalar `d.name = 'a'; d.name.x = 1` | Converts scalar to `{'a': {'x': 1}}` |
| Compare scalar proxy `d.count > 10` | Delegates to underlying value |
| Format scalar proxy `f'{d.name:>10}'` | Delegates to underlying value |
| Dict in a list `[{'a': 1}]` | Dict becomes `dotdict` |
| `d.to_dict()` | Recursively unwraps to plain `dict`/`list` |
| `repr(d)` / `print(d)` | Indented JSON via `json.dumps(indent=2)` |
| `bool(d)` | `False` when empty (inherited from `dict`) |
| `d.keys()` / `d.values()` / `d.items()` | Standard dict behavior |
| Dict key shadows method name (e.g., `items`) | Dict value takes priority |
| `d == None` when `d` is missing-key proxy | `True` (proxy compares equal to `None`) |
| `d.freeze()` then mutate | Raises `AttributeError` |
| `d.on_change(path, cb)` then set path | Fires `cb(path, new_value)` |
| `d.diff(other)` | Returns `{path: {'from': ..., 'to': ...}}` |
| `d.find(name)` | Returns sorted list of dot-paths to matches |

---

## Limitations

- Keys that clash with `dotdict` method names (e.g., `keys`, `values`, `items`, `update`, `copy`, `get`, `to_dict`) shadow the method when accessed via dot notation. Use bracket notation to access the method, or key the data under a different name.
- Keys starting with `_` cannot be accessed via dot notation — use bracket notation instead.
- `hasattr(d, 'missing')` returns `True` because `__getattr__` returns a `_Missing` proxy instead of raising `AttributeError`.
