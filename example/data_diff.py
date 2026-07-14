"""
example: data_diff.py — Compare configs, find keys, batch set/delete
"""

from easydotdict import dotdict

v1 = dotdict({"app": {"name": "MyApp", "debug": True, "port": 3000}})
v2 = dotdict({"app": {"name": "MyApp", "debug": False, "port": 8080, "version": "2.0"}})

d = v1.diff(v2)
for path, ch in d.items():
    print(f"  {path}: {ch['from']} -> {ch['to']}")

print()

v1.patch(d)
print(f"After patch: debug={v1.app.debug}, port={v1.app.port}, version={v1.app.version}")

cfg = dotdict()
cfg.set_many({"a.b.c": 1, "x.y": 2, "data.value": 42})
print(f"\nset_many: a.b.c={cfg.a.b.c}, x.y={cfg.x.y}, data.value={cfg.data.value}")

print(f"\nKeys containing 'y': {cfg.find('y')}")
print(f"Keys containing 'value': {cfg.find('value')}")

cfg.delete("x.y", "a.b")
print(f"\nAfter delete: has 'x.y'={cfg.has('x.y')}, has 'a'={cfg.has('a')}, has 'a.b.c'={cfg.has('a.b.c')}")
