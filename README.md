# Doom Nightfall

Doom Nightfall is a small first-person shooter built with Python and Pygame. It takes the classic raycasting approach: move through a maze, fight demons, collect supplies, and clear the sector.

It runs at 60 FPS and includes animated enemies, weapon animations, sound effects, music, pickups, difficulty settings, and win and game-over screens.

## Running the game

### From Python

Install Python 3.10 or newer, then install Pygame from the project folder:

```bash
pip install pygame
```

Start the game with:

```bash
python main.py
```

### Windows executable

The Windows build is distributed as `DoomNightfall-windows.zip`. Download the ZIP from the GitHub release, extract it completely, and open `DoomNightfall/DoomNightfall.exe`.

Do not upload or run only `DoomNightfall.exe`. This is a PyInstaller folder build and it needs the `_internal` folder beside the executable, including `python313.dll` and the bundled game resources. If `_internal` is missing or incomplete, Windows shows a `python313.dll` or `LoadLibrary` error.

To build it yourself, install PyInstaller and run:

```bash
pip install pyinstaller
pyinstaller --clean --noconfirm DoomNightfall.spec
```

PyInstaller puts the finished build in `dist/DoomNightfall/`.

## Controls

| Action | Key or button |
| --- | --- |
| Move | `W`, `A`, `S`, `D` |
| Aim | Mouse |
| Fire | Left mouse button |
| Reload | `R` |
| Interact | `E` |
| Pause or resume | `P` |
| Change difficulty | `F1` Recruit, `F2` Marine, `F3` Nightmare |
| Start the mission | `Enter`, `Space`, or left click |
| Restart after the mission | `R`, `Enter`, or the replay button |
| Quit | `Esc` |

## Project layout

- `main.py` starts the game loop.
- `player.py` handles movement, aiming, health, and shooting.
- `raycasting.py` draws the 3D-style view.
- `npc.py` handles enemy behavior and animations.
- `object_renderer.py` draws textures, the HUD, menus, and effects.
- `resources/` holds the textures, sprites, sounds, and music.
- `DoomNightfall.spec` defines the PyInstaller build.

## Notes

The game needs the `resources` folder. When you run from source, start it from the project directory. When you use the executable, keep the whole `dist/DoomNightfall` folder together instead of moving only the `.exe` file.

Sorry HackClub for this VibeCoded Readme.md