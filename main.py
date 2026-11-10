"""NVIDIA RTX ONLY - a tiny first-person ray-tracing demo.

Controls:
    W/A/S/D       move and strafe
    Left/Right    turn
    Mouse/Space   fire
    R             restart
    Esc           quit

This intentionally has no graphics dependencies: Tkinter is used only as a
presentation surface while the scene is rendered by the ray tracer below.
"""

import math
import random
import time
import tkinter as tk


MAP = [
    "################",
    "#..............#",
    "#..##....##....#",
    "#..............#",
    "#....#.........#",
    "#....#....##...#",
    "#..............#",
    "#..##..........#",
    "#..............#",
    "#......##......#",
    "#..............#",
    "################",
]
SCREEN_W, SCREEN_H = 960, 600
RAYS = 256
FOV = math.pi / 3


def wall_at(x, y):
    ix, iy = int(x), int(y)
    return iy < 0 or iy >= len(MAP) or ix < 0 or ix >= len(MAP[0]) or MAP[iy][ix] == "#"


def shade(rgb, amount):
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(rgb[0] * amount))),
        max(0, min(255, int(rgb[1] * amount))),
        max(0, min(255, int(rgb[2] * amount))),
    )


class Target:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.health = 2
        self.alive = True
        self.flash = 0.0


class RTXAssault:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RTX ASSAULT // NVIDIA RAY TRACING ONLY")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root, width=SCREEN_W, height=SCREEN_H, bg="#05070c",
            highlightthickness=0, cursor="none",
        )
        self.canvas.pack()
        self.keys = set()
        self.player = [2.5, 6.0, 0.0]
        self.health, self.score, self.shots = 100, 0, 0
        self.cooldown, self.muzzle, self.damage_flash = 0.0, 0.0, 0.0
        self.state = "playing"
        self.targets = [
            Target(12.5, 2.5), Target(9.5, 4.5), Target(13.0, 8.5),
            Target(4.5, 9.0), Target(7.5, 7.0),
        ]
        self.last = time.perf_counter()
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.root.bind("<Button-1>", lambda _event: self.fire())
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<FocusOut>", lambda _event: self.keys.clear())
        self.root.focus_force()
        self.loop()

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "space":
            self.fire()
        elif key == "r" and self.state != "playing":
            self.restart()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def restart(self):
        self.player = [2.5, 6.0, 0.0]
        self.health, self.score, self.shots = 100, 0, 0
        self.cooldown = self.muzzle = self.damage_flash = 0.0
        for target in self.targets:
            target.health, target.alive, target.flash = 2, True, 0.0
        self.state = "playing"

    def move(self, dx, dy):
        px, py, angle = self.player
        # Sliding collision keeps movement responsive around the simple arena.
        if not wall_at(px + dx, py):
            px += dx
        if not wall_at(px, py + dy):
            py += dy
        self.player[0], self.player[1] = px, py

    def update(self, dt):
        self.cooldown = max(0.0, self.cooldown - dt)
        self.muzzle = max(0.0, self.muzzle - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)
        if self.state != "playing":
            return
        turn = (("right" in self.keys) - ("left" in self.keys)) * 2.2 * dt
        self.player[2] = (self.player[2] + turn) % (math.pi * 2)
        forward = ("w" in self.keys) - ("s" in self.keys)
        strafe = ("d" in self.keys) - ("a" in self.keys)
        if forward or strafe:
            angle = self.player[2]
            speed = 3.2 * dt
            self.move(
                (math.cos(angle) * forward + math.cos(angle + math.pi / 2) * strafe)
                * speed,
                (math.sin(angle) * forward + math.sin(angle + math.pi / 2) * strafe)
                * speed,
            )
        for target in self.targets:
            if not target.alive:
                continue
            target.flash = max(0.0, target.flash - dt)
            distance = math.hypot(target.x - self.player[0], target.y - self.player[1])
            if distance < 8 and self.has_line_of_sight(target.x, target.y):
                self.health -= 8 * dt
                self.damage_flash = 0.12
        if self.health <= 0:
            self.state = "dead"
        elif not any(target.alive for target in self.targets):
            self.state = "clear"

    def has_line_of_sight(self, tx, ty):
        distance = math.hypot(tx - self.player[0], ty - self.player[1])
        steps = max(1, int(distance * 12))
        for step in range(1, steps):
            t = step / steps
            if wall_at(self.player[0] + (tx - self.player[0]) * t,
                       self.player[1] + (ty - self.player[1]) * t):
                return False
        return True

    def fire(self):
        if self.state != "playing" or self.cooldown:
            return
        self.cooldown, self.muzzle = 0.22, 0.08
        self.shots += 1
        angle = self.player[2]
        best, best_distance = None, float("inf")
        for target in self.targets:
            if not target.alive:
                continue
            dx, dy = target.x - self.player[0], target.y - self.player[1]
            distance = math.hypot(dx, dy)
            difference = (math.atan2(dy, dx) - angle + math.pi) % (math.pi * 2) - math.pi
            if abs(difference) < 0.055 and distance < best_distance and self.has_line_of_sight(target.x, target.y):
                best, best_distance = target, distance
        if best:
            best.health -= 1
            best.flash = 0.12
            if best.health <= 0:
                best.alive = False
                self.score += 100

    def wall_distance(self, angle):
        px, py = self.player[0], self.player[1]
        ray_x, ray_y = math.cos(angle), math.sin(angle)
        map_x, map_y = int(px), int(py)
        delta_x = abs(1 / ray_x) if ray_x else 1e30
        delta_y = abs(1 / ray_y) if ray_y else 1e30
        if ray_x < 0:
            step_x, side_x = -1, (px - map_x) * delta_x
        else:
            step_x, side_x = 1, (map_x + 1 - px) * delta_x
        if ray_y < 0:
            step_y, side_y = -1, (py - map_y) * delta_y
        else:
            step_y, side_y = 1, (map_y + 1 - py) * delta_y
        side = 0
        for _ in range(64):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
            if wall_at(map_x, map_y):
                distance = side_x - delta_x if side == 0 else side_y - delta_y
                return max(0.01, distance), side
        return 20.0, side

    def render(self):
        c = self.canvas
        c.delete("frame")
        # Layered sky and floor gradients provide a readable sci-fi atmosphere.
        for row in range(0, SCREEN_H // 2, 12):
            ratio = row / (SCREEN_H / 2)
            c.create_rectangle(
                0, row, SCREEN_W, row + 13,
                fill=shade((5, 11, 27), 0.72 + ratio * 0.5),
                outline="", tags="frame",
            )
        for row in range(SCREEN_H // 2, SCREEN_H, 12):
            ratio = (row - SCREEN_H / 2) / (SCREEN_H / 2)
            c.create_rectangle(
                0, row, SCREEN_W, row + 13,
                fill=shade((10, 19, 28), 0.65 + ratio * 0.55),
                outline="", tags="frame",
            )
        # Distant stars and a neon horizon make the space outside the arena visible.
        for x, y, size in ((88, 106, 2), (196, 74, 1), (318, 142, 2),
                           (702, 86, 2), (842, 130, 1), (908, 62, 1)):
            c.create_oval(x, y, x + size, y + size, fill="#9adfff", outline="", tags="frame")
        c.create_line(0, SCREEN_H // 2, SCREEN_W, SCREEN_H // 2,
                      fill="#256782", width=2, tags="frame")
        self.render_floor_grid()
        depths = []
        for column in range(RAYS):
            camera = (column + 0.5) / RAYS - 0.5
            ray_angle = self.player[2] + camera * FOV
            distance, side = self.wall_distance(ray_angle)
            corrected = distance * math.cos(camera * FOV)
            wall_height = min(SCREEN_H * 1.8, SCREEN_H / corrected)
            top = SCREEN_H / 2 - wall_height / 2
            bottom = SCREEN_H / 2 + wall_height / 2
            light = max(0.12, 1.0 - corrected / 14) * (0.72 if side else 1.0)
            color = shade((44, 153, 182), light)
            x0 = int(column * SCREEN_W / RAYS)
            x1 = int((column + 1) * SCREEN_W / RAYS) + 1
            c.create_rectangle(x0, top, x1, bottom, fill=color, outline="", tags="frame")
            # Alternating wall panels and a bright upper edge sell the material.
            if column % 7 in (0, 1):
                c.create_rectangle(x0, top + wall_height * .12, x1, bottom,
                                   fill=shade((22, 89, 113), light), outline="", tags="frame")
            c.create_line(x0, top, x1, top, fill=shade((119, 227, 238), light * 1.2),
                          width=1, tags="frame")
            depths.append(corrected)
        self.render_targets(depths)
        self.render_weapon()
        self.render_hud()

    def render_floor_grid(self):
        c = self.canvas
        horizon = SCREEN_H / 2
        # Perspective guide lines are clipped visually by the low contrast floor.
        for offset in range(20, 420, 26):
            y = horizon + offset * offset / 210
            if y < SCREEN_H:
                c.create_line(0, y, SCREEN_W, y, fill="#1b3c4b", tags="frame")
        for x in range(-900, 1900, 90):
            c.create_line(SCREEN_W / 2, horizon, x, SCREEN_H, fill="#163342", tags="frame")

    def render_targets(self, depths):
        c = self.canvas
        visible = []
        for target in self.targets:
            if not target.alive:
                continue
            dx, dy = target.x - self.player[0], target.y - self.player[1]
            distance = math.hypot(dx, dy)
            relative = (math.atan2(dy, dx) - self.player[2] + math.pi) % (math.pi * 2) - math.pi
            if abs(relative) > FOV / 2 + 0.15 or not self.has_line_of_sight(target.x, target.y):
                continue
            screen_x = SCREEN_W / 2 + math.tan(relative) / math.tan(FOV / 2) * SCREEN_W / 2
            size = min(260, SCREEN_H / distance * 0.78)
            ray = int(screen_x / SCREEN_W * RAYS)
            if 0 <= ray < len(depths) and distance < depths[ray] + 0.2:
                visible.append((distance, screen_x, size, target))
        for _, x, size, target in sorted(visible, reverse=True):
            y = SCREEN_H / 2 + size * 0.1
            color = "#ffffff" if target.flash else "#e5484d"
            glow = "#ff4056" if target.flash else "#7b1d3b"
            for scale, alpha_color in ((1.8, "#24172e"), (1.45, "#422039")):
                c.create_oval(x - size * .27 * scale, y - size * .44 * scale,
                              x + size * .27 * scale, y + size * .1 * scale,
                              fill=alpha_color, outline="", tags="frame")
            self.canvas.create_oval(x - size * .27, y - size * .44, x + size * .27, y + size * .1,
                                    fill=color, outline=glow, width=3, tags="frame")
            self.canvas.create_rectangle(x - size * .2, y + size * .06, x + size * .2, y + size * .55,
                                         fill="#9e2737", outline="#ff7070", width=2, tags="frame")
            self.canvas.create_line(x - size * .18, y + size * .15, x + size * .18, y + size * .15,
                                    fill="#ffb14e", width=max(1, int(size * .025)), tags="frame")
            self.canvas.create_oval(x - size * .12, y - size * .25, x - size * .04, y - size * .17,
                                    fill="#111111", outline="", tags="frame")
            self.canvas.create_oval(x + size * .04, y - size * .25, x + size * .12, y - size * .17,
                                    fill="#111111", outline="", tags="frame")

    def render_weapon(self):
        c = self.canvas
        recoil = -18 if self.muzzle else 0
        c.create_polygon(430, SCREEN_H, 475, 390 + recoil, 560, 390 + recoil, 610, SCREEN_H,
                         fill="#10151f", outline="#5b6677", width=3, tags="frame")
        c.create_polygon(463, SCREEN_H, 490, 445 + recoil, 540, 445 + recoil, 576, SCREEN_H,
                         fill="#293448", outline="#7185a0", width=2, tags="frame")
        c.create_rectangle(486, 420 + recoil, 548, 470 + recoil, fill="#283142",
                           outline="#a6c5dc", width=2, tags="frame")
        c.create_line(495, 435 + recoil, 540, 435 + recoil, fill="#57e5f5", width=3, tags="frame")
        c.create_oval(508, 448 + recoil, 524, 464 + recoil, fill="#e1fbff", outline="", tags="frame")
        if self.muzzle:
            c.create_oval(460, 315, 578, 435, fill="#6c352c", outline="", tags="frame")
            c.create_polygon(480, 400, 518, 292, 556, 400, fill="#f3c94b",
                             outline="#fff0a3", width=3, tags="frame")

    def render_hud(self):
        c = self.canvas
        c.create_text(24, 22, text="RTX ASSAULT", anchor="nw", fill="#9fe7ff",
                      font=("Consolas", 17, "bold"), tags="frame")
        c.create_text(24, 51, text="NVIDIA RAY TRACING ONLY", anchor="nw", fill="#5bc4e8",
                      font=("Consolas", 10), tags="frame")
        c.create_text(SCREEN_W - 24, 24, text=f"TARGETS  {sum(t.alive for t in self.targets)}  //  SCORE  {self.score:04d}",
                      anchor="ne", fill="#d7e8ef", font=("Consolas", 12), tags="frame")
        c.create_rectangle(24, SCREEN_H - 32, 224, SCREEN_H - 20, fill="#222b35", outline="", tags="frame")
        c.create_rectangle(24, SCREEN_H - 32, 24 + max(0, self.health) * 2, SCREEN_H - 20,
                           fill="#e5484d" if self.health < 40 else "#59d48b", outline="", tags="frame")
        c.create_text(24, SCREEN_H - 52, text=f"VITALS {max(0, int(self.health)):03d}     WASD MOVE  •  ← → TURN  •  CLICK / SPACE FIRE",
                      anchor="sw", fill="#d7e8ef", font=("Consolas", 10), tags="frame")
        c.create_line(SCREEN_W / 2 - 9, SCREEN_H / 2, SCREEN_W / 2 + 9, SCREEN_H / 2,
                      fill="#b9f4ff", tags="frame")
        c.create_line(SCREEN_W / 2, SCREEN_H / 2 - 9, SCREEN_W / 2, SCREEN_H / 2 + 9,
                      fill="#b9f4ff", tags="frame")
        if self.damage_flash:
            c.create_rectangle(0, 0, SCREEN_W, SCREEN_H, outline="#ff334d", width=8, tags="frame")
        if self.state != "playing":
            title = "ARENA CLEAR" if self.state == "clear" else "SIGNAL LOST"
            c.create_rectangle(270, 245, 690, 360, fill="#080d16", outline="#5bc4e8", width=2, tags="frame")
            c.create_text(SCREEN_W / 2, 278, text=title, fill="#d9f7ff", font=("Consolas", 26, "bold"), tags="frame")
            c.create_text(SCREEN_W / 2, 323, text="PRESS R TO REDEPLOY", fill="#5bc4e8", font=("Consolas", 12), tags="frame")

    def loop(self):
        now = time.perf_counter()
        dt = min(0.05, now - self.last)
        self.last = now
        self.update(dt)
        self.render()
        self.root.after(16, self.loop)


if __name__ == "__main__":
    RTXAssault().root.mainloop()
