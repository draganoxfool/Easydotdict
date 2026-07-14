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
        self._parent[self._key] = dd
        return _Missing(dd[self._value], name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            dd = dotdict()
            dd[self._value] = dotdict()
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
        self._parent[self._key] = dd
        return dd[self._value][key]

    def __setitem__(self, key, value):
        dd = dotdict()
        dd[self._value] = dotdict()
        dd[self._value][key] = _wrap(value)
        self._parent[self._key] = dd

    def __delitem__(self, key):
        raise KeyError(key)



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
    for key, value in source.items():
        if key in target and isinstance(target[key], dotdict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


class dotdict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in list(super().items()):
            if isinstance(value, dict) and not isinstance(value, dotdict):
                super().__setitem__(key, dotdict(value))
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
        dict.__setitem__(self, key, _wrap(value))

    def __delattr__(self, key):
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
        dict.__setitem__(self, key, _wrap(value))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2, default=str)

    def __str__(self):
        return self.__repr__()

    def to_dict(self):
        result = {}
        for key, value in self.items():
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
            if hasattr(other, 'items'):
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

    def get(self, key, default=None):
        if key in self:
            return dict.__getitem__(self, key)
        return default

    def dig(self, path):
        keys = path.split('.')
        current = self
        for key in keys:
            if isinstance(current, dict):
                try:
                    current = dict.__getitem__(current, key)
                except KeyError:
                    return None
            else:
                return None
        return current

    def put(self, path, value):
        keys = path.split('.')
        current = self
        for key in keys[:-1]:
            if key not in current:
                current[key] = dotdict()
            current = current[key]
        current[keys[-1]] = value

    def has(self, path):
        keys = path.split('.')
        current = self
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = dict.__getitem__(current, key)
            else:
                return False
        return True

    def flatten(self, prefix=''):
        result = {}
        for key, value in self.items():
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
