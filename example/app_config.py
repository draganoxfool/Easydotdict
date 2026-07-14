"""
example: app_config.py — Persist and edit app config using a JSON file
Usage:   python app_config.py          # show current config
         python app_config.py --reset  # reset to defaults
"""

from easydotdict import dotdict
from json import dump, load
from pathlib import Path
from sys import argv

CONFIG_FILE = Path("config.json")

DEFAULTS = dotdict({
    "app": {
        "theme": "dark",
        "locale": "en-US",
    },
    "editor": {
        "font_size": 14,
        "tab_spaces": 4,
        "word_wrap": True,
    },
    "shortcuts": {
        "save": "Ctrl+S",
        "find": "Ctrl+F",
    },
})

if "--reset" in argv:
    with open(CONFIG_FILE, "w") as f:
        dump(DEFAULTS.to_dict(), f, indent=2)
    print("Config reset to defaults.")
    config = DEFAULTS

elif CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        config = dotdict(load(f))
    print("Loaded existing config.")

else:
    config = DEFAULTS
    with open(CONFIG_FILE, "w") as f:
        dump(config.to_dict(), f, indent=2)
    print("Created default config.")

theme = config.app.theme
font = config.editor.font_size
wrap = config.editor.word_wrap

print(f"Theme: {theme}  |  Font size: {font}  |  Word wrap: {wrap}")
print(f"Shortcuts: save={config.shortcuts.save}  find={config.shortcuts.find}")
