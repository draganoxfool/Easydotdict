import json


class _Missing:
    def __init__(self, parent, key):
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_key', key)

    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError(key)
        return _Missing(self, key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self._materialize().__setitem__(key, value)

    def __setitem__(self, key, value):
        self._materialize().__setitem__(key, value)

    def __delattr__(self, key):
        self._materialize().__delitem__(key)

    def __bool__(self):
        return False

    def __eq__(self, other):
        if other is None:
            return True
        return NotImplemented

    def __ne__(self, other):
        if other is None:
            return False
        return NotImplemented

    def __repr__(self):
        return 'None'

    def __str__(self):
        return 'None'

    def _materialize(self):
        path = []
        obj = self
        while isinstance(obj, _Missing):
            path.append(obj._key)
            obj = obj._parent
        current = obj
        for key in reversed(path):
            if key not in current:
                current[key] = dotdict()
                _set_parent(current[key], current, key)
            current = current[key]
        return current


class _ValueProxy:
    def __init__(self, value, parent, key):
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_key', key)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        dd = dotdict()
        dd[self._value] = dotdict()
        _set_parent(dd[self._value], dd, self._value)
        self._parent[self._key] = dd
        return _Missing(dd[self._value], name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            if _is_frozen(self._parent):
                raise AttributeError("Cannot modify frozen dotdict")
            dd = dotdict()
            dd[self._value] = dotdict()
            _set_parent(dd[self._value], dd, self._value)
            dd[self._value][name] = _wrap(value)
            self._parent[self._key] = dd

    def __delattr__(self, name):
        raise AttributeError(name)

    def __bool__(self):
        return bool(self._value)

    def __eq__(self, other):
        if other is None:
            return False
        return self._value == other

    def __ne__(self, other):
        if other is None:
            return True
        return self._value != other

    def __lt__(self, other):   return self._value < other
    def __le__(self, other):   return self._value <= other
    def __gt__(self, other):   return self._value > other
    def __ge__(self, other):   return self._value >= other

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        return str(self._value)

    def __format__(self, spec):
        return format(self._value, spec)

    def __hash__(self):
        return hash(self._value)

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, item):
        return item in self._value

    def __getitem__(self, key):
        dd = dotdict()
        dd[self._value] = dotdict()
        _set_parent(dd[self._value], dd, self._value)
        self._parent[self._key] = dd
        return dd[self._value][key]

    def __setitem__(self, key, value):
        if _is_frozen(self._parent):
            raise KeyError("Cannot modify frozen dotdict")
        dd = dotdict()
        dd[self._value] = dotdict()
        _set_parent(dd[self._value], dd, self._value)
        dd[self._value][key] = _wrap(value)
        self._parent[self._key] = dd

    def __delitem__(self, key):
        raise KeyError(key)


class _Cursor:
    def __init__(self, target):
        object.__setattr__(self, '_target', target)

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return getattr(self._target, key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            setattr(self._target, key, value)

    def __delattr__(self, key):
        delattr(self._target, key)

    def __getitem__(self, key):
        return self._target[key]

    def __setitem__(self, key, value):
        self._target[key] = value

    def __delitem__(self, key):
        del self._target[key]

    def __repr__(self):
        return repr(self._target)

    def __str__(self):
        return str(self._target)


def _set_parent(child, parent, key):
    if isinstance(child, dotdict):
        object.__setattr__(child, '_dd_parent', parent)
        object.__setattr__(child, '_dd_key', key)


def _get_root(dd):
    while True:
        try:
            parent = object.__getattribute__(dd, '_dd_parent')
        except AttributeError:
            return dd
        dd = parent


def _path_of(dd, key):
    parts = []
    cur = dd
    while True:
        try:
            parent = object.__getattribute__(cur, '_dd_parent')
            k = object.__getattribute__(cur, '_dd_key')
        except AttributeError:
            break
        parts.append(k)
        cur = parent
    parts.reverse()
    parts.append(str(key))
    return '.'.join(parts)


def _is_frozen(dd):
    try:
        return object.__getattribute__(_get_root(dd), '_dd_frozen')
    except AttributeError:
        return False


def _notify_change(dd, key, value):
    root = _get_root(dd)
    try:
        cbs = object.__getattribute__(root, '_dd_callbacks')
    except AttributeError:
        return
    path = _path_of(dd, key)
    for cb_path, callbacks in cbs.items():
        if path == cb_path or path.startswith(cb_path + '.'):
            for cb in callbacks:
                cb(path, value)


def _wrap(value):
    if isinstance(value, _ValueProxy):
        value = value._value
    if isinstance(value, dict) and not isinstance(value, dotdict):
        return dotdict(value)
    elif isinstance(value, list):
        return _convert_list(value)
    return value


def _convert_list(lst):
    result = []
    for item in lst:
        if isinstance(item, dict) and not isinstance(item, dotdict):
            result.append(dotdict(item))
        elif isinstance(item, list):
            result.append(_convert_list(item))
        else:
            result.append(item)
    return result


def _deep_merge(target, source):
    for key in dict.keys(source):
        value = source[key] if not isinstance(source, dotdict) else dict.__getitem__(source, key)
        if key in target and isinstance(target[key], dotdict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


class dotdict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in list(super().items()):
            if isinstance(value, dict) and not isinstance(value, dotdict):
                converted = dotdict(value)
                _set_parent(converted, self, key)
                super().__setitem__(key, converted)
            elif isinstance(value, list):
                super().__setitem__(key, _convert_list(value))

    _SCALAR_TYPES = (str, int, float, bool, bytes, type(None))

    def __getattribute__(self, key):
        if key.startswith('_'):
            return super().__getattribute__(key)
        try:
            value = dict.__getitem__(self, key)
            if isinstance(value, self._SCALAR_TYPES):
                return _ValueProxy(value, self, key)
            return value
        except KeyError:
            return super().__getattribute__(key)

    def __getattr__(self, key):
        return _Missing(self, key)

    def __setattr__(self, key, value):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        value = _wrap(value)
        _set_parent(value, self, key)
        dict.__setitem__(self, key, value)
        _notify_change(self, key, value)

    def __delattr__(self, key):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        try:
            dict.__delitem__(self, key)
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return None

    def __setitem__(self, key, value):
        if _is_frozen(self):
            raise KeyError("Cannot modify frozen dotdict")
        value = _wrap(value)
        _set_parent(value, self, key)
        dict.__setitem__(self, key, value)
        _notify_change(self, key, value)

    def __delitem__(self, key):
        if _is_frozen(self):
            raise KeyError("Cannot modify frozen dotdict")
        super().__delitem__(key)

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2, default=str)

    def __str__(self):
        return self.__repr__()

    def to_dict(self):
        result = {}
        for key in dict.keys(self):
            value = dict.__getitem__(self, key)
            if isinstance(value, dotdict):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, dotdict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def copy(self):
        return self.clone()

    def clone(self):
        return dotdict(self.to_dict())

    def update(self, other=None, **kwargs):
        if other is not None:
            if isinstance(other, dict):
                _deep_merge(self, other)
            else:
                for k, v in other:
                    self[k] = v
        for k, v in kwargs.items():
            _deep_merge_items = {k: v}
            _deep_merge(self, _deep_merge_items)

    def merge(self, other):
        _deep_merge(self, other)
        return self

    def get(self, path, default=None):
        if '.' in path:
            return self.dig(path) if self.has(path) else default
        if path in self:
            return dict.__getitem__(self, path)
        return default

    def set_many(self, items):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        for path, value in items.items():
            self.put(path, value)
        return self

    def delete(self, *paths):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        for path in paths:
            keys = path.split('.')
            current = self
            for key in keys[:-1]:
                if isinstance(current, list) and key.isdigit():
                    idx = int(key)
                    if idx < len(current):
                        current = current[idx]
                    else:
                        current = None
                        break
                else:
                    current = current[key]
                if current is None:
                    break
            if current is not None:
                last = keys[-1]
                if isinstance(current, list) and last.isdigit():
                    idx = int(last)
                    if idx < len(current):
                        del current[idx]
                else:
                    del current[last]
        return self

    def dig(self, path):
        keys = path.split('.')
        current = self
        for key in keys:
            if isinstance(current, dict):
                try:
                    current = dict.__getitem__(current, key)
                except KeyError:
                    return None
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                if idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                return None
        return current

    def put(self, path, value):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        keys = path.split('.')
        current = self
        for key in keys[:-1]:
            if isinstance(current, list) and key.isdigit():
                idx = int(key)
                if idx >= len(current):
                    current.append(dotdict())
                    _set_parent(current[-1], current, idx)
                current = current[idx]
            else:
                if isinstance(current, dict) and key not in current:
                    current[key] = dotdict()
                    _set_parent(current[key], current, key)
                current = current[key]
        last = keys[-1]
        value = _wrap(value)
        if isinstance(current, list) and last.isdigit():
            idx = int(last)
            if idx >= len(current):
                current.append(value)
            else:
                current[idx] = value
            if isinstance(value, dotdict):
                _set_parent(value, current, idx)
            _notify_change(current, idx, value)
        else:
            _set_parent(value, current, last)
            dict.__setitem__(current, last, value)
            _notify_change(current, last, value)

    def has(self, path):
        keys = path.split('.')
        current = self
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = dict.__getitem__(current, key)
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                if idx < len(current):
                    current = current[idx]
                else:
                    return False
            else:
                return False
        return True

    def cursor(self, path, create=False):
        if create:
            self.put(path, dotdict())
        target = self.dig(path)
        if target is None:
            raise KeyError(f"Path '{path}' not found")
        if not isinstance(target, (dotdict, dict)):
            raise TypeError(f"Cannot create cursor on non-dict at '{path}'")
        if not isinstance(target, dotdict):
            target = dotdict(target)
        return _Cursor(target)

    def find(self, name):
        results = []
        def _search(obj, prefix):
            for key in dict.keys(obj):
                value = dict.__getitem__(obj, key)
                full = f'{prefix}.{key}' if prefix else str(key)
                if key == name:
                    results.append(full)
                if isinstance(value, dotdict):
                    _search(value, full)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        item_full = f'{full}.{i}'
                        if isinstance(item, dotdict):
                            _search(item, item_full)
        _search(self, '')
        return results

    def diff(self, other):
        a_flat = self.flatten()
        b_flat = other.flatten() if isinstance(other, dotdict) else dotdict(other).flatten()
        all_keys = set(a_flat) | set(b_flat)
        changes = {}
        for k in all_keys:
            av = a_flat.get(k, _MISSING)
            bv = b_flat.get(k, _MISSING)
            if av != bv:
                changes[k] = {'from': None if av is _MISSING else av, 'to': None if bv is _MISSING else bv}
        return changes

    def patch(self, changes):
        if _is_frozen(self):
            raise AttributeError("Cannot modify frozen dotdict")
        for path, change in changes.items():
            if 'to' in change:
                if change['to'] is None and self.has(path):
                    self.delete(path)
                elif change['to'] is not None:
                    self.put(path, change['to'])
        return self

    def expect(self, schema):
        for path, expected_type in schema.items():
            value = self.dig(path)
            if value is None:
                raise KeyError(f"Missing required path '{path}'")
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    raise TypeError(f"Path '{path}' expected {expected_type}, got {type(value).__name__}")
            elif not isinstance(value, expected_type):
                raise TypeError(f"Path '{path}' expected {expected_type.__name__}, got {type(value).__name__}")
        return self

    def on_change(self, path, callback):
        root = _get_root(self)
        try:
            cbs = object.__getattribute__(root, '_dd_callbacks')
        except AttributeError:
            object.__setattr__(root, '_dd_callbacks', {})
            cbs = object.__getattribute__(root, '_dd_callbacks')
        cbs.setdefault(path, []).append(callback)
        return self

    def freeze(self):
        object.__setattr__(_get_root(self), '_dd_frozen', True)
        return self

    def unfreeze(self):
        object.__setattr__(_get_root(self), '_dd_frozen', False)
        return self

    @property
    def is_frozen(self):
        try:
            return object.__getattribute__(_get_root(self), '_dd_frozen')
        except AttributeError:
            return False

    def flatten(self, prefix=''):
        result = {}
        for key in dict.keys(self):
            value = dict.__getitem__(self, key)
            full_key = f'{prefix}.{key}' if prefix else str(key)
            if isinstance(value, dotdict):
                result.update(value.flatten(prefix=full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_key = f'{full_key}.{i}'
                    if isinstance(item, dotdict):
                        result.update(item.flatten(prefix=item_key))
                    else:
                        result[item_key] = item
            else:
                result[full_key] = value
        return result

    @classmethod
    def unflatten(cls, data):
        root = {}
        for dotted_key, value in data.items():
            parts = dotted_key.split('.')
            current = root
            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)
                if is_last:
                    current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        return cls(cls._lists_from_dict(root))

    @staticmethod
    def _lists_from_dict(d):
        if not isinstance(d, dict):
            return d
        keys = list(d.keys())
        if keys and all(isinstance(k, str) and k.isdigit() for k in keys):
            max_idx = max(int(k) for k in keys)
            lst = [None] * (max_idx + 1)
            for k in keys:
                idx = int(k)
                lst[idx] = dotdict._lists_from_dict(d[k])
            return lst
        return {k: dotdict._lists_from_dict(v) for k, v in d.items()}

    def is_empty(self):
        return len(self) == 0


_MISSING = object()
