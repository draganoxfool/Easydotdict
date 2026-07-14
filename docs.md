# easydotdict Documentation

## Table of Contents

1.  [Overview](#overview)
2.  [Installation](#installation)
3.  [Getting Started](#getting-started)
4.  [Core Concepts](#core-concepts)
    - [Dot & Bracket Notation](#dot--bracket-notation)
    - [Safe Missing-Key Access](#safe-missing-key-access)
    - [Auto-Vivification](#auto-vivification)
    - [Scalar Auto-Conversion](#scalar-auto-conversion)
    - [Auto-Conversion of Nested Structures](#auto-conversion-of-nested-structures)
    - [Pretty-Printing](#pretty-printing)
5.  [Working with Deep Paths](#working-with-deep-paths)
    - [Reading with `dig()` and `get()`](#reading-with-dig-and-get)
    - [Writing with `put()`](#writing-with-put)
    - [Checking Existence with `has()`](#checking-existence-with-has)
6.  [Transforming Structures](#transforming-structures)
    - [Flatten & Unflatten](#flatten--unflatten)
    - [Deep Merge: `update()` and `merge()`](#deep-merge-update-and-merge)
    - [Round-Trip with `to_dict()`](#round-trip-with-to_dict)
7.  [Advanced Operations](#advanced-operations)
    - [Batch Write with `set_many()`](#batch-write-with-set_many)
    - [Batch Delete with `delete()`](#batch-delete-with-delete)
    - [Comparing Objects with `diff()` and `patch()`](#comparing-objects-with-diff-and-patch)
    - [Searching with `find()`](#searching-with-find)
    - [Type Validation with `expect()`](#type-validation-with-expect)
    - [Change Tracking with `on_change()`](#change-tracking-with-on_change)
    - [Freezing Objects with `freeze()` / `unfreeze()`](#freezing-objects-with-freeze--unfreeze)
    - [Cursors for Focused Access](#cursors-for-focused-access)
8.  [Decorators](#decorators)
    - [`@dotdictify`](#dotdictify)
    - [`@defaults`](#defaults)
    - [`@expect_schema`](#expect_schema)
    - [`@freeze`](#freeze-1)
9.  [Standard dict Compatibility](#standard-dict-compatibility)
10. [Edge Cases & Behaviour](#edge-cases--behaviour)
11. [Limitations](#limitations)

---

## Overview

`easydotdict` is a zero-dependency Python library that transforms ordinary dictionaries into navigable, resilient data structures. It provides dot-notation access, safe handling of missing keys, automatic nesting of assigned values, and pretty-printed output — all while remaining a fully-compatible subclass of `dict`.

The library is designed for any scenario where you work with deeply nested dictionaries: API responses, configuration files, JSON documents, or database records. Instead of chaining bracket access (`data['user']['profile']['name']`) and guarding against `KeyError`, you write `data.user.profile.name` and missing keys return `None` rather than raising exceptions.

---

## Installation

```bash
pip install easydotdict
```

The library has zero external dependencies. Python 3.8 or later is required.

---

## Getting Started

The core export is the `dotdict` class. Wrap any dictionary and immediately access its contents with dot notation:

```python
from easydotdict import dotdict

response = dotdict({"user": {"profile": {"name": "Alice"}}})
print(response.user.profile.name)  # Alice
```

Every nested `dict` inside the wrapped data is also converted to a `dotdict`, so the convenience extends arbitrarily deep.

---

## Core Concepts

### Dot & Bracket Notation

You may access and modify values using either style interchangeably:

```python
d = dotdict()
d.user.name = "Alice"
d.user["age"] = 30

print(d.user.name)   # Alice
print(d["user"].age) # 30
```

Bracket notation is useful when the key is dynamic or when it contains characters (such as hyphens or leading underscores) that are invalid in Python identifiers.

### Safe Missing-Key Access

Accessing a key that does not exist returns `None` instead of raising `KeyError` or `AttributeError`. This mirrors the safety of JavaScript's optional chaining and eliminates the need for explicit guards:

```python
d = dotdict({"a": 1})
print(d.user.email)  # None
print(d["b"])        # None
print(d.get("b"))    # None
```

The returned value is technically a lightweight proxy object that behaves identically to `None` in boolean contexts, comparisons, and truth checks.

### Auto-Vivification

Assigning a value through a chain of missing keys automatically creates the intermediate structure. This allows deep nested assignment in a single expression:

```python
d = dotdict()
d.config.database.host = "localhost"
d.config.database.port = 5432

# Result: {'config': {'database': {'host': 'localhost', 'port': 5432}}}
```

Each intermediate key becomes a new `dotdict`, so the chain is fully navigable at every level.

### Scalar Auto-Conversion

When you assign an attribute to a value that is currently a scalar (string, integer, float, boolean, or `None`), the scalar is automatically promoted to a nested dictionary keyed by its own string representation:

```python
d = dotdict()
d.name = "Alice"
d.name.character = 5

# Result: {'name': {'Alice': {'character': 5}}}
```

This behaviour applies to any scalar type:

```python
d = dotdict()
d.count = 42
d.count.meaning = "everything"

# Result: {'count': {'42': {'meaning': 'everything'}}}
```

Scalar proxies also delegate comparison operators and format specifications to the underlying value:

```python
d = dotdict()
d.count = 42

print(d.count > 10)      # True
print(f"{d.count:05d}")  # 00042
```

This enables type-specific formatting (zero-padding, alignment, precision) without manually extracting the raw value.

### Auto-Conversion of Nested Structures

When you initialise a `dotdict` with a plain `dict`, every nested `dict` encountered during traversal is automatically wrapped into a `dotdict`. Lists that contain dictionaries also receive this treatment:

```python
data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
d = dotdict(data)

print(d.users[0].name)       # Alice
print(type(d.users[0]))      # <class 'easydotdict.dotdict'>
```

This means you never need to manually wrap intermediate results — the conversion cascades on access.

### Pretty-Printing

Both `repr()` and `str()` produce indented JSON output via the standard library's `json.dumps(indent=2)`. This makes debugging and logging significantly more readable:

```python
d = dotdict({"name": "Alice", "scores": [90, 95]})
print(d)
# {
#   "name": "Alice",
#   "scores": [
#     90,
#     95
#   ]
# }
```

---

## Working with Deep Paths

Deep path methods accept a dot-separated string that describes a traversal into nested keys. They treat numeric segments (e.g., `0`, `1`) as list indices, allowing uniform access to both dictionary and list structures.

### Reading with `dig()` and `get()`

`dig(path)` traverses the path and returns the value, or `None` if any segment is missing:

```python
d = dotdict({"user": {"name": "Alice", "addresses": [{"city": "Berlin"}]}})

print(d.dig("user.name"))                # Alice
print(d.dig("user.addresses.0.city"))    # Berlin
print(d.dig("user.addresses.1.city"))    # None (index out of range)
```

`get(path, default=None)` works identically but also accepts a single key (without dots) as a convenience:

```python
print(d.get("user.name"))                # Alice
print(d.get("user.email", "n/a"))        # n/a
```

The `get()` method correctly distinguishes between a key whose value is `None` and a key that is genuinely missing, returning the default only in the latter case.

### Writing with `put()`

`put(path, value)` traverses the path, creating intermediate `dotdict` objects (or extending lists) as needed, then assigns the value:

```python
d = dotdict()
d.put("server.host", "localhost")
d.put("server.ports.0", 8080)
d.put("server.ports.1", 9090)

print(d.server.host)       # localhost
print(d.server.ports[0])   # 8080
```

### Checking Existence with `has()`

`has(path)` returns `True` if the path resolves to an existing value, `False` otherwise:

```python
d = dotdict({"user": {"name": "Alice"}})

print(d.has("user.name"))   # True
print(d.has("user.email"))  # False
print(d.has("user.name.first"))  # False ("name" is a string, not a dict)
```

---

## Transforming Structures

### Flatten & Unflatten

`flatten()` reduces a nested `dotdict` to a single-level dictionary where each key is a dot-separated path. List items are indexed numerically:

```python
d = dotdict({"user": {"name": "Alice", "scores": [90, 95]}})
flat = d.flatten()

# flat == {
#     "user.name": "Alice",
#     "user.scores.0": 90,
#     "user.scores.1": 95,
# }
```

`unflatten(data)` is a class method that reverses the operation, converting flat dot-separated keys back into a nested `dotdict`:

```python
restored = dotdict.unflatten({"a.b.c": 1, "x.0": "first"})
print(restored.a.b.c)  # 1
print(restored.x[0])   # first
```

Numeric keys become list indices; alphabetical keys become dictionary keys.

### Deep Merge: `update()` and `merge()`

`update(other)` performs a recursive deep merge of `other` into the current `dotdict`. Existing keys are preserved unless they are overridden by the merge:

```python
d = dotdict({"user": {"name": "Alice", "age": 30}})
d.update({"user": {"email": "alice@example.com"}})

print(d.user.email)  # alice@example.com
print(d.user.name)   # Alice (preserved)
```

`merge(other)` behaves identically but returns `self`, enabling method chaining:

```python
d.merge({"settings": {"debug": True}}).merge({"settings": {"theme": "dark"}})
```

### Round-Trip with `to_dict()`

`to_dict()` recursively converts all nested `dotdict` objects back into plain `dict` and `list` instances. This is essential when serialising to JSON or passing data to code that expects standard Python types:

```python
d = dotdict({"user": {"name": "Alice"}})
plain = d.to_dict()

# plain == {"user": {"name": "Alice"}}
# type(plain["user"]) == dict
```

---

## Advanced Operations

### Batch Write with `set_many()`

`set_many(items)` accepts a dictionary of `{path: value}` pairs and applies each via `put()`. This is useful for applying a set of overrides from configuration files, environment variables, or CLI arguments:

```python
d = dotdict()
d.set_many({
    "database.host": "localhost",
    "database.port": 5432,
    "logging.level": "debug",
})

print(d.database.host)   # localhost
print(d.logging.level)   # debug
```

### Batch Delete with `delete()`

`delete(*paths)` removes one or more paths from the structure. It silently ignores paths that do not exist:

```python
d = dotdict({"a": {"b": 1, "c": 2}, "x": 3})
d.delete("a.b", "x")

# d == {"a": {"c": 2}}
```

### Comparing Objects with `diff()` and `patch()`

`diff(other)` compares the current `dotdict` with another and returns a dictionary describing every difference. Each entry maps a dot-separated path to a `{"from": old_value, "to": new_value}` record. Paths present in only one side use `None` for the missing value:

```python
v1 = dotdict({"app": {"name": "MyApp", "debug": True}})
v2 = dotdict({"app": {"name": "MyApp", "debug": False, "version": "2.0"}})

changes = v1.diff(v2)
# {
#   "app.debug":     {"from": True,  "to": False},
#   "app.version":   {"from": None,  "to": "2.0"},
# }
```

`patch(changes)` applies the output of `diff()` (or any compatible dictionary) back to the current object. This enables patterns like state comparison, migration, or rollback:

```python
v1.patch(changes)
print(v1.app.version)  # 2.0
print(v1.app.debug)    # False
```

### Searching with `find()`

`find(name)` recursively searches the entire structure for keys whose name matches the given string and returns a sorted list of dot-separated paths to each match:

```python
d = dotdict({
    "a": {"b": 1, "c": {"b": 2}},
    "x": {"b": 3},
})

print(d.find("b"))
# ["a.b", "a.c.b", "x.b"]
```

This is particularly useful for locating all occurrences of a field in a large, irregular data structure — for example, finding every `"id"`, `"email"`, or `"language"` field in an API response.

### Type Validation with `expect()`

`expect(schema)` validates the types of values at runtime. The schema is a dictionary mapping dot-separated paths to expected types (or tuples of acceptable types). The method raises `KeyError` if a required path is missing, or `TypeError` if the value's type does not match:

```python
user = dotdict({"name": "Alice", "age": 30})
user.expect({"name": str, "age": int})  # passes

user.expect({"email": str})             # KeyError: missing required path 'email'

bad = dotdict({"name": "Bob", "age": "unknown"})
bad.expect({"age": int})                # TypeError: path 'age' expected int, got str
```

This is useful at system boundaries — validating an API response or configuration file shape before proceeding with business logic.

### Change Tracking with `on_change()`

`on_change(path, callback)` registers a callback that is invoked whenever the value at the specified path is modified via `__setitem__` or `put()`. The callback receives the path string and the new value:

```python
config = dotdict()
config.app.debug = True

def alert(path, value):
    print(f"[config] {path} changed to {value}")

config.on_change("app.debug", alert)
config.app.debug = False  # prints: [config] app.debug changed to False
```

Multiple callbacks may be registered for the same path. The system tracks ownership through parent references, so mutations on nested `dotdict` objects propagate upward correctly.

### Freezing Objects with `freeze()` / `unfreeze()`

Freezing renders a `dotdict` immutable. Any attempt to set, delete, or modify an attribute or item raises `AttributeError`:

```python
d = dotdict({"key": "value"})
d.freeze()

d.key = "new"     # raises AttributeError
d.new_key = "x"   # raises AttributeError
del d.key          # raises AttributeError

d.unfreeze()
d.key = "new"     # succeeds

print(d.is_frozen)  # False
```

Freezing is valuable in production environments where a configuration object must remain constant after initialisation, or when returning data from a function that should not be mutated by the caller.

### Cursors for Focused Access

A cursor is a lightweight view that exposes a nested portion of a `dotdict` as if it were the root. All reads and writes through the cursor affect the original object directly — no copy is made:

```python
d = dotdict({"database": {"host": "localhost", "port": 5432}})
db = d.cursor("database")

print(db.host)     # localhost
db.port = 8080     # modifies d.database.port
print(d.database.port)  # 8080
```

The optional `create=True` parameter auto-creates intermediate paths if they do not exist:

```python
d = dotdict()
c = d.cursor("server.config", create=True)
c.timeout = 30
# d now == {"server": {"config": {"timeout": 30}}}
```

Cursors are useful for passing a focused slice of a large configuration or state object to a function without exposing or copying the entire structure.

---

## Decorators

Decorators are imported directly from the `easydotdict` package and integrate with existing function signatures:

```python
from easydotdict import dotdictify, defaults, expect_schema, freeze
```

### `@dotdictify`

Converts the first positional argument from a plain `dict` into a `dotdict` before the function body executes. This eliminates the need to call `dotdict()` at every call site:

```python
@dotdictify
def process_user(data):
    print(data.user.name)  # data is a dotdict

process_user({"user": {"name": "Alice"}})
```

### `@defaults`

Merges default values into the first positional argument (which should be a `dotdict`) before the function runs. Only missing keys are populated — existing values are never overwritten:

```python
@defaults(page=1, limit=20)
def list_items(params):
    print(params.page)   # uses caller's value or falls back to 1
    print(params.limit)  # uses caller's value or falls back to 20

list_items(dotdict({"page": 5}))        # page=5, limit=20
list_items(dotdict())                    # page=1, limit=20
```

### `@expect_schema`

Validates the first positional argument against a schema at call time, raising `TypeError` or `KeyError` if validation fails. The schema format is identical to that used by `dotdict.expect()`:

```python
@expect_schema({"name": str, "age": int})
def save_user(user):
    # Only reached if validation passes
    print(f"Saving {user.name}")

save_user(dotdict({"name": "Alice", "age": 30}))  # OK
save_user(dotdict({"name": 123}))                  # TypeError
```

### `@freeze`

Freezes the return value of the decorated function if it is a `dotdict`. This prevents callers from accidentally mutating a returned configuration or state object:

```python
@freeze
def load_config():
    return dotdict({"debug": True, "port": 8080})

cfg = load_config()
# cfg is frozen — cfg.debug = False raises AttributeError
```

---

## Standard dict Compatibility

Because `dotdict` inherits from `dict`, all standard dictionary methods work as expected:

- `keys()`, `values()`, `items()`
- `pop(key, *args)`
- `clear()`
- `len()`, `in`, `iter()`
- `bool()` — returns `False` when empty
- `copy()` — returns a deep copy as a new `dotdict`
- `is_empty()` — convenience method for `len(d) == 0`

---

## Edge Cases & Behaviour

| Scenario | Behaviour |
|---|---|
| Access missing key via bracket `d["x"]` | Returns `None` |
| Access missing key via dot `d.x` | Returns `None` (via a `_Missing` proxy) |
| Set `d.a.b.c = value` with missing intermediates | Auto-creates intermediate `dotdict` objects |
| Assign attribute to scalar `d.name = "a"; d.name.x = 1` | Converts scalar to `{"a": {"x": 1}}` |
| Compare scalar proxy `d.count > 10` | Delegates to the underlying value |
| Format scalar proxy `f"{d.name:>10}"` | Delegates to the underlying value |
| Dict inside a list `[{"a": 1}]` | Dict becomes a `dotdict` on access |
| `d.to_dict()` | Recursively unwraps to plain `dict` / `list` |
| `repr(d)` / `print(d)` | Indented JSON via `json.dumps(indent=2)` |
| `bool(d)` | `False` when empty (inherited from `dict`) |
| `d.keys()`, `d.values()`, `d.items()` | Standard dict behaviour |
| Dict key shadows a method name (e.g., `items`) | Data value takes priority in dot notation |
| `d == None` when `d` is a missing-key proxy | `True` — the proxy compares equal to `None` |
| `d.freeze()` followed by mutation | Raises `AttributeError` |
| `d.on_change(path, cb)` followed by set | Fires `cb(path, new_value)` |
| `d.diff(other)` | Returns `{path: {"from": ..., "to": ...}}` |
| `d.find(name)` | Returns sorted list of dot-paths to matching keys |

---

## Limitations

- **Method name shadowing:** Keys that coincide with `dotdict` method names (`keys`, `values`, `items`, `update`, `copy`, `get`, `to_dict`) shadow the method when accessed via dot notation. Use bracket notation (`d["keys"]`) to access the data value, or avoid using such names as keys.
- **Underscore-prefixed keys:** Keys beginning with `_` are reserved for internal use and cannot be accessed via dot notation. Use bracket notation (`d["_private"]`) instead.
- **`hasattr` behaviour:** `hasattr(d, "missing")` returns `True` because `__getattr__` returns a `_Missing` proxy rather than raising `AttributeError`. Use `"missing" in d` or `d.has("missing")` for existence checks.
