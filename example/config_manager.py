"""
example: config_manager.py — Validate, watch, freeze, and bulk-override app config
"""

from json import dump, load
from pathlib import Path
from easydotdict import dotdict

CONFIG_FILE = Path("app_settings.json")

DEFAULTS = dotdict({
    "server": {"host": "0.0.0.0", "port": 8080},
    "database": {"url": "sqlite:///app.db", "pool_size": 5},
    "logging": {"level": "debug", "file": "/var/log/app.log"},
})

config = dotdict()
config.update(DEFAULTS)

if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        config.update(load(f))

# expect — Validate the loaded config shape
config.expect({
    "server.host": str,
    "server.port": int,
    "database.url": str,
    "logging.level": str,
})

# on_change — Auto-persist any config change to disk
def auto_save(path, value):
    with open(CONFIG_FILE, "w") as f:
        dump(config.to_dict(), f, indent=2)
    print(f"  Saved change: {path} = {value}")

config.on_change("server.host", auto_save)
config.on_change("server.port", auto_save)
config.on_change("logging.level", auto_save)

# set_many — Apply CLI/env overrides in bulk
overrides = {
    "server.host": "0.0.0.0",
    "database.pool_size": 10,
    "logging.level": "info",
}
config.set_many(overrides)

# freeze — Lock config in production
config.freeze()
try:
    config.server.port = 9090
except AttributeError:
    print("  Frozen — config is locked")
