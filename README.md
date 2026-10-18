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

The ready-to-run build is in `dist/DoomNightfall/`. Open `DoomNightfall.exe` from that folder. Leave the `_internal` folder beside it; the executable needs those game resources and runtime files.

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
