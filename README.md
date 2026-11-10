# RTX Assault

A tiny first-person sci-fi shooter built from scratch in Python. **RTX Assault**
uses a software ray-casting renderer and Tkinter for its presentation surface,
so it has no external graphics dependencies.

## Features

- Ray-cast first-person rendering with neon sci-fi visuals
- WASD movement, strafing, and keyboard turning
- Mouse or Space shooting with muzzle-flash feedback
- Line-of-sight checks and wall collision
- Enemy health, player health, score, and target tracking
- Arena-clear and game-over states with restart support
- Custom HUD, crosshair, floor grid, weapon, and visual effects

## Requirements

- Python 3.10 or newer
- Tkinter, included with most standard Python installations

## Run

```bash
python main.py
```

## Controls

| Input | Action |
| --- | --- |
| `W` / `S` | Move forward / backward |
| `A` / `D` | Strafe left / right |
| `Left` / `Right` | Turn |
| Mouse click / `Space` | Fire |
| `R` | Restart after victory or defeat |
| `Esc` | Quit |

## How to Play

Find and eliminate every target in the arena. Targets must be visible and in
the crosshair to take damage. Stay alert: visible targets within range will
also reduce your health. Clear all targets before your health reaches zero.

## Technology

- Python
- Tkinter Canvas
- Standard-library math, random, and time modules
- Custom 2D ray-casting and depth-aware sprite rendering

## License

This project is available for learning and demonstration purposes.
