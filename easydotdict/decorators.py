from functools import wraps
from .easydotdict import dotdict


def dotdictify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and isinstance(args[0], dict) and not isinstance(args[0], dotdict):
            args = (dotdict(args[0]),) + args[1:]
        return func(*args, **kwargs)
    return wrapper


def defaults(_defaults=None, **kwargs):
    merged = {}
    if _defaults:
        merged.update(_defaults)
    merged.update(kwargs)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                target = args[0]
                if isinstance(target, dotdict):
                    for path, value in _flatten_dict(merged).items():
                        if not target.has(path):
                            target.put(path, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def expect_schema(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                target = args[0]
                if isinstance(target, dotdict):
                    target.expect(schema)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def freeze(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dotdict):
            result.freeze()
        return result
    return wrapper


def _flatten_dict(d, prefix=''):
    result = {}
    for key, value in d.items():
        full = f'{prefix}.{key}' if prefix else str(key)
        if isinstance(value, dict):
            result.update(_flatten_dict(value, full))
        else:
            result[full] = value
    return result
