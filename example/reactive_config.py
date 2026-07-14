"""
example: reactive_config.py — Watch for changes, use cursors, freeze config
"""

from easydotdict import dotdict

config = dotdict()
config.database.host = "localhost"
config.database.port = 5432
config.app.debug = True

changes = []
config.on_change("database.host", lambda p, v: changes.append(f"host -> {v}"))
config.on_change("app.debug", lambda p, v: changes.append(f"debug -> {v}"))

config.database.host = "prod.example.com"
config.app.debug = False

for c in changes:
    print(f"Change: {c}")

db = config.cursor("database", create=True)
db.host = "new.host.com"
db.port = 8080

print(f"Cursored: {config.database.host}:{config.database.port}")

config.freeze()
try:
    config.app.debug = True
except AttributeError:
    print("Frozen — can't modify")
