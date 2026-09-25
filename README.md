# Foldery

Desktop folder-icon manager for **Windows 11** and **macOS**. Assign a custom icon to one folder or many, from a pack, by drag-and-drop, or with a double-click.

## Install

```bash
pip install -r requirements.txt
```

On macOS you also need Xcode Command Line Tools (`iconutil`):

```bash
xcode-select --install
```

Optional: point Foldery at an icon pack before launch.

```bash
# Windows
set FOLDER_ICONS=E:\Media\Icons\Pack1
python -m foldery

# macOS / Linux
export FOLDER_ICONS=~/Icons/Pack1
python3 -m foldery
```

Run from this directory (`desktop/`) so the `foldery` package is on `PYTHONPATH`. The pack can also be chosen from the toolbar after launch.

Writing `desktop.ini` into protected Windows folders needs an elevated process. Foldery will say so if it cannot write.

## Features

- Drive / volume tree on the left; no need to hunt for the root
- Drag an icon from the gallery onto a folder to assign it immediately
- Drop `.ico` / `.png` / `.jpg` / `.icns` files onto the gallery to copy them into the pack
- Double-click an icon to apply it to the current selection
- Multi-select folders (Ctrl/Cmd-click); one assign writes all of them
- Search the gallery by name
- Light / dark theme; Mica on Windows 11, vibrancy on macOS

## Languages

UI strings live in `foldery/i18n/locales/*.json`. English is the fallback. Russian ships as a second locale so the wiring is obvious.

To add a language, copy `en.json` to `de.json` (or whatever code you want), fill in `_meta`, translate the values, and restart. Foldery lists every JSON file in that folder — no code changes.

```json
{
  "_meta": {
    "code": "de",
    "name": "German",
    "nativeName": "Deutsch"
  },
  "app.name": "Foldery",
  "preview.assign": "Symbol zuweisen"
}
```

Missing keys fall back to English. `FOLDERY_LANG=ru` selects a locale at startup; the toolbar switcher changes it at runtime.

Placeholders use `{name}` / `{n}` style: `"Assigned “{name}” to {n} folder(s)"`.

## Layout

```
foldery/
  app.py                 # QApplication + composition root
  config.py              # names, env, platform flags
  domain/errors.py       # IconAssignError
  i18n/catalog.py        # translator; auto-discovers locale JSON
  platforms/             # OS backends behind FolderIconBackend
    windows.py           # desktop.ini + SHChangeNotify
    macos.py             # NSWorkspace / osascript + iconutil
    unsupported.py
  services/
    icon_pack.py         # list / copy pack files
    assignment.py        # assign / remove, independent of Qt
  ui/                    # window, theme, widgets
```

The window talks to `AssignmentService` and `IconPack`. It does not import Win32 or AppKit. Swap or test a backend without touching the UI.

## Notes

- Windows: `IconResource` uses `%FOLDER_ICONS%\file.ico` when the file lives in the current pack, so the reference stays portable.
- macOS: Finder embeds the icon; there is no path back to the original file, so the preview only reports that a custom icon is set.
- Linux: the window runs, assignment does not. There is no Explorer/Finder equivalent that Foldery targets.
