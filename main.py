"""
Frog Jumping Game
A fun arcade-style game where you control a frog jumping across lily pads
to avoid obstacles and reach the other side.

Controls:
  Arrow Keys / WASD - Move the frog
  Space - Jump
  R - Restart (after game over)
  Q / ESC - Quit
"""

import tkinter as tk
import random
import math
import time


class Frog:
    """The player-controlled frog character."""

    def __init__(self, x, y, canvas_width, canvas_height):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.speed = 5
        self.jumping = False
        self.jump_height = 0
        self.jump_speed = 0
        self.direction = "up"  # up, down, left, right
        self.anim_frame = 0
        self.anim_timer = 0

    def update(self):
        # Handle jumping physics
        if self.jumping:
            self.jump_height += self.jump_speed
            self.jump_speed -= 1.2  # gravity
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jumping = False
                self.jump_speed = 0

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Set direction
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        # Boundary checking
        self.x = max(0, min(self.canvas_width - self.width, new_x))
        self.y = max(0, min(self.canvas_height - self.height, new_y))

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_speed = 18

    def draw(self, canvas):
        draw_x = self.x
        draw_y = self.y - self.jump_height

        # Shadow (shows ground position)
        if self.jumping:
            canvas.create_oval(
                self.x, self.y + self.height - 5,
                self.x + self.width, self.y + self.height + 5,
                fill="gray", stipple="gray50"
            )

        # Body
        body_color = "#2E7D32"
        belly_color = "#66BB6A"
        canvas.create_oval(
            draw_x + 5, draw_y + 5,
            draw_x + self.width - 5, draw_y + self.height - 5,
            fill=body_color, outline="#1B5E20", width=2
        )

        # Belly
        canvas.create_oval(
            draw_x + 10, draw_y + 12,
            draw_x + self.width - 10, draw_y + self.height - 8,
            fill=belly_color
        )

        # Eyes
        eye_offset_x = 0
        eye_offset_y = 0
        if self.direction == "left":
            eye_offset_x = -3
        elif self.direction == "right":
            eye_offset_x = 3
        elif self.direction == "down":
            eye_offset_y = 3

        # Left eye
        canvas.create_oval(
            draw_x + 10 + eye_offset_x, draw_y + 5 + eye_offset_y,
            draw_x + 20 + eye_offset_x, draw_y + 15 + eye_offset_y,
            fill="white", outline="black", width=1
        )
        canvas.create_oval(
            draw_x + 13 + eye_offset_x, draw_y + 8 + eye_offset_y,
            draw_x + 17 + eye_offset_x, draw_y + 12 + eye_offset_y,
            fill="black"
        )

        # Right eye
        canvas.create_oval(
            draw_x + 20 + eye_offset_x, draw_y + 5 + eye_offset_y,
            draw_x + 30 + eye_offset_x, draw_y + 15 + eye_offset_y,
            fill="white", outline="black", width=1
        )
        canvas.create_oval(
            draw_x + 23 + eye_offset_x, draw_y + 8 + eye_offset_y,
            draw_x + 27 + eye_offset_x, draw_y + 12 + eye_offset_y,
            fill="black"
        )

        # Legs (animated)
        leg_offset = math.sin(self.anim_frame * math.pi / 2) * 5
        if not self.jumping:
            # Back legs
            canvas.create_oval(
                draw_x - 3 + leg_offset, draw_y + self.height - 10,
                draw_x + 10 + leg_offset, draw_y + self.height + 5,
                fill=body_color, outline="#1B5E20", width=1
            )
            canvas.create_oval(
                draw_x + self.width - 10 - leg_offset, draw_y + self.height - 10,
                draw_x + self.width + 3 - leg_offset, draw_y + self.height + 5,
                fill=body_color, outline="#1B5E20", width=1
            )


class LilyPad:
    """A lily pad that the frog can land on."""

    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.wobble = 0
        self.wobble_speed = random.uniform(0.02, 0.05)

    def update(self):
        self.wobble += self.wobble_speed

    def draw(self, canvas):
        wobble_offset = math.sin(self.wobble) * 2
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2 + wobble_offset

        # Main pad
        canvas.create_oval(
            self.x, self.y + wobble_offset,
            self.x + self.size, self.y + self.size + wobble_offset,
            fill="#4CAF50", outline="#2E7D32", width=2
        )

        # Veins
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x2 = center_x + math.cos(rad) * (self.size // 2 - 5)
            y2 = center_y + wobble_offset + math.sin(rad) * (self.size // 2 - 5)
            canvas.create_line(
                center_x, center_y + wobble_offset,
                x2, y2, fill="#388E3C", width=1
            )

        # Cutout notch
        canvas.create_arc(
            center_x - 5, center_y - 5 + wobble_offset,
            center_x + 5, center_y + 5 + wobble_offset,
            start=0, extent=360, style=tk.ARC,
            fill="#006994", outline="#006994", width=2
        )


class Obstacle:
    """Moving obstacles like snails or fish."""

    def __init__(self, x, y, speed, obstacle_type="snail"):
        self.x = x
        self.y = y
        self.speed = speed
        self.type = obstacle_type
        self.width = 35
        self.height = 25
        self.direction = 1
        self.anim_frame = 0

    def update(self, canvas_width):
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x >= canvas_width - self.width:
            self.direction *= -1
        self.anim_frame += 0.1

    def draw(self, canvas):
        if self.type == "snail":
            # Shell
            canvas.create_oval(
                self.x + 5, self.y - 10,
                self.x + 25, self.y + 10,
                fill="#8D6E63", outline="#5D4037", width=2
            )
            # Shell spiral
            canvas.create_arc(
                self.x + 10, self.y - 5,
                self.x + 20, self.y + 5,
                start=0, extent=270, style=tk.ARC,
                fill="#A1887F", width=2
            )
            # Body
            body_wave = math.sin(self.anim_frame) * 2
            canvas.create_oval(
                self.x + 20, self.y + body_wave,
                self.x + self.width, self.y + self.height + body_wave,
                fill="#BCAAA4", outline="#8D6E63", width=1
            )
            # Eyes
            canvas.create_oval(
                self.x + 28, self.y - 5 + body_wave,
                self.x + 32, self.y - 1 + body_wave,
                fill="black"
            )
        elif self.type == "fish":
            # Body
            canvas.create_oval(
                self.x + 5, self.y,
                self.x + self.width - 5, self.y + self.height,
                fill="#FF7043", outline="#D84315", width=2
            )
            # Tail
            tail_wave = math.sin(self.anim_frame * 2) * 5
            canvas.create_polygon(
                self.x + self.width - 5, self.y + self.height // 2 + tail_wave,
                self.x + self.width + 10, self.y - 5,
                self.x + self.width + 10, self.y + self.height + 5,
                fill="#FF7043", outline="#D84315", width=1
            )
            # Eye
            eye_x = self.x + 10 if self.direction > 0 else self.x + self.width - 15
            canvas.create_oval(
                eye_x, self.y + 5,
                eye_x + 6, self.y + 11,
                fill="white", outline="black", width=1
            )
            canvas.create_oval(
                eye_x + 2, self.y + 7,
                eye_x + 4, self.y + 9,
                fill="black"
            )


class Coin:
    """Collectible coins for scoring."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.collected = False
        self.anim_frame = random.random() * math.pi * 2

    def update(self):
        self.anim_frame += 0.05

    def draw(self, canvas):
        if self.collected:
            return

        bob_offset = math.sin(self.anim_frame) * 3
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2 + bob_offset

        # Coin body
        canvas.create_oval(
            self.x, self.y + bob_offset,
            self.x + self.size, self.y + self.size + bob_offset,
            fill="#FFD54F", outline="#FF8F00", width=2
        )
        # Dollar sign
        canvas.create_text(
            center_x, center_y + bob_offset,
            text="$", fill="#FF8F00", font=("Arial", 10, "bold")
        )


class Particle:
    """Visual effect particles."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.color = color
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # gravity
        self.life -= self.decay

    def draw(self, canvas):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        canvas.create_oval(
            self.x, self.y,
            self.x + self.size, self.y + self.size,
            fill=self.color, stipple="gray%d" % (50 + int(self.life * 50))
        )


class FrogJumpGame:
    """Main game class for the Frog Jumping game."""

    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_state = "playing"  # playing, game_over, win
        self.coins_needed = 5  # coins to advance level
        self.coins_collected = 0
        self.combo = 0
        self.combo_timer = 0
        self.screen_shake = 0

        # Create main window
        self.root = tk.Tk()
        self.root.title("🐸 Frog Jumping Adventure 🐸")
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            bg="#006994",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Game objects
        self.frog = Frog(
            self.window_width // 2 - 20,
            self.window_height - 80,
            self.window_width,
            self.window_height
        )
        self.lily_pads = []
        self.obstacles = []
        self.coins = []
        self.particles = []

        # Input handling
        self.keys = {}
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<Escape>", self.on_escape)

        # UI elements
        self.setup_ui()
        self.generate_level()

        # Start game loop
        self.running = True
        self.game_loop()

    def setup_ui(self):
        """Create UI overlay elements."""
        # Score label
        self.score_label = self.canvas.create_text(
            20, 20, text="Score: 0", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        # Lives label
        self.lives_label = self.canvas.create_text(
            20, 45, text="Lives: ❤️❤️❤️", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        # Level label
        self.level_label = self.canvas.create_text(
            20, 70, text="Level: 1", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        # Coins label
        self.coins_label = self.canvas.create_text(
            20, 95, text="Coins: 0/5", fill="#FFD54F",
            font=("Arial", 16, "bold"), anchor="w"
        )
        # Combo label
        self.combo_label = self.canvas.create_text(
            self.window_width - 20, 20, text="", fill="#FFEB3B",
            font=("Arial", 14, "bold"), anchor="e"
        )
        # Instructions
        self.instructions_label = self.canvas.create_text(
            self.window_width // 2, 20, text="Arrow Keys: Move | Space: Jump | R: Restart | Q: Quit",
            fill="white", font=("Arial", 11), anchor="n"
        )

    def generate_level(self):
        """Generate lily pads, obstacles, and coins for the current level."""
        self.lily_pads = []
        self.obstacles = []
        self.coins = []

        # Generate lily pads in rows
        rows = 4 + self.level
        pads_per_row = 5 + self.level

        for row in range(rows):
            y = 100 + row * 100
            for col in range(pads_per_row):
                x = random.randint(50, self.window_width - 100)
                size = random.randint(40, 60)
                self.lily_pads.append(LilyPad(x, y, size))

        # Generate obstacles
        num_obstacles = 3 + self.level * 2
        for _ in range(num_obstacles):
            x = random.randint(0, self.window_width - 50)
            y = random.randint(120, self.window_height - 100)
            speed = random.uniform(1, 2 + self.level * 0.5)
            obstacle_type = random.choice(["snail", "fish"])
            self.obstacles.append(Obstacle(x, y, speed, obstacle_type))

        # Generate coins
        num_coins = self.coins_needed + random.randint(2, 5)
        for _ in range(num_coins):
            x = random.randint(30, self.window_width - 50)
            y = random.randint(80, self.window_height - 100)
            self.coins.append(Coin(x, y))

    def on_key_press(self, event):
        """Handle key press events."""
        self.keys[event.keysym.lower()] = True

        if event.keysym == "space":
            if self.game_state == "playing":
                self.frog.jump()
            elif self.game_state in ("game_over", "win"):
                self.restart_game()

        if event.keysym.lower() == "r":
            self.restart_game()

    def on_key_release(self, event):
        """Handle key release events."""
        self.keys[event.keysym.lower()] = False

    def on_escape(self, event):
        """Handle escape key to quit."""
        self.running = False
        self.root.quit()

    def handle_input(self):
        """Process keyboard input for movement."""
        dx, dy = 0, 0

        if self.keys.get("left") or self.keys.get("a"):
            dx -= 1
        if self.keys.get("right") or self.keys.get("d"):
            dx += 1
        if self.keys.get("up") or self.keys.get("w"):
            dy -= 1
        if self.keys.get("down") or self.keys.get("s"):
            dy += 1

        if dx != 0 or dy != 0:
            self.frog.move(dx, dy)

    def spawn_particles(self, x, y, color, count=10):
        """Spawn visual effect particles."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def check_collisions(self):
        """Check for collisions between game objects."""
        frog_rect = (
            self.frog.x, self.frog.y,
            self.frog.x + self.frog.width,
            self.frog.y + self.frog.height
        )

        # Check coin collection
        for coin in self.coins:
            if coin.collected:
                continue

            coin_rect = (
                coin.x, coin.y,
                coin.x + coin.size,
                coin.y + coin.size
            )

            if self.rects_overlap(frog_rect, coin_rect):
                coin.collected = True
                self.coins_collected += 1
                self.combo += 1
                self.combo_timer = 120  # 2 seconds at 60fps

                # Combo scoring
                combo_multiplier = min(self.combo, 10)
                points = 10 * combo_multiplier
                self.score += points

                # Visual feedback
                self.spawn_particles(
                    coin.x + coin.size // 2,
                    coin.y + coin.size // 2,
                    "#FFD54F", 15
                )

                # Check level completion
                if self.coins_collected >= self.coins_needed:
                    self.advance_level()

        # Check obstacle collision
        for obstacle in self.obstacles:
            obstacle_rect = (
                obstacle.x, obstacle.y - 10,
                obstacle.x + obstacle.width,
                obstacle.y + obstacle.height
            )

            if self.rects_overlap(frog_rect, obstacle_rect):
                self.hit_obstacle()
                break

    def rects_overlap(self, rect1, rect2):
        """Check if two rectangles overlap."""
        return not (
            rect1[2] < rect2[0] or
            rect1[0] > rect2[2] or
            rect1[3] < rect2[1] or
            rect1[1] > rect2[3]
        )

    def hit_obstacle(self):
        """Handle the frog being hit by an obstacle."""
        self.lives -= 1
        self.combo = 0
        self.screen_shake = 10

        # Visual feedback
        self.spawn_particles(
            self.frog.x + self.frog.width // 2,
            self.frog.y + self.frog.height // 2,
            "#FF5252", 20
        )

        if self.lives <= 0:
            self.game_state = "game_over"

    def advance_level(self):
        """Advance to the next level."""
        self.level += 1
        self.coins_collected = 0
        self.coins_needed = 5 + self.level * 2
        self.score += 100 * self.level

        # Visual celebration
        for _ in range(30):
            x = random.randint(0, self.window_width)
            y = random.randint(0, self.window_height)
            color = random.choice(["#FFD54F", "#4CAF50", "#2196F3", "#E91E63"])
            self.spawn_particles(x, y, color, 5)

        # Check win condition
        if self.level > 5:
            self.game_state = "win"
            return

        # Generate new level
        self.generate_level()

    def update(self):
        """Update all game objects."""
        if self.game_state != "playing":
            return

        # Handle input
        self.handle_input()

        # Update frog
        self.frog.update()

        # Update lily pads
        for pad in self.lily_pads:
            pad.update()

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.window_width)

        # Update coins
        for coin in self.coins:
            coin.update()

        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()

        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

        # Check collisions
        self.check_collisions()

    def draw(self):
        """Draw all game objects."""
        self.canvas.delete("all")

        # Screen shake offset
        shake_x = 0
        shake_y = 0
        if self.screen_shake > 0:
            shake_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_y = random.randint(-self.screen_shake, self.screen_shake)

        # Apply screen shake to all drawing by offsetting coordinates
        def sx(x):
            return x + shake_x

        def sy(y):
            return y + shake_y

        # Draw water background with wave pattern
        for y in range(0, self.window_height, 40):
            wave_offset = math.sin(y * 0.02 + time.time() * 0.001) * 5
            self.canvas.create_line(
                sx(0), sy(y + wave_offset),
                sx(self.window_width), sy(y + wave_offset),
                fill="#00838F", width=2, dash=(20, 10)
            )

        # Draw lily pads (with shake applied internally)
        for pad in self.lily_pads:
            # Temporarily offset lily pad position for shake
            orig_x, orig_y = pad.x, pad.y
            pad.x += shake_x
            pad.y += shake_y
            pad.draw(self.canvas)
            pad.x, pad.y = orig_x, orig_y

        # Draw coins (with shake)
        for coin in self.coins:
            orig_x, orig_y = coin.x, coin.y
            coin.x += shake_x
            coin.y += shake_y
            coin.draw(self.canvas)
            coin.x, coin.y = orig_x, orig_y

        # Draw obstacles (with shake)
        for obstacle in self.obstacles:
            orig_x, orig_y = obstacle.x, obstacle.y
            obstacle.x += shake_x
            obstacle.y += shake_y
            obstacle.draw(self.canvas)
            obstacle.x, obstacle.y = orig_x, orig_y

        # Draw frog (with shake)
        orig_fx, orig_fy = self.frog.x, self.frog.y
        self.frog.x += shake_x
        self.frog.y += shake_y
        self.frog.draw(self.canvas)
        self.frog.x, self.frog.y = orig_fx, orig_fy

        # Draw particles (with shake)
        for particle in self.particles:
            orig_px, orig_py = particle.x, particle.y
            particle.x += shake_x
            particle.y += shake_y
            particle.draw(self.canvas)
            particle.x, particle.y = orig_px, orig_py

        # Draw UI
        self.canvas.create_text(
            sx(20), sy(20), text=f"Score: {self.score}", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        hearts = "❤️" * self.lives + "🖤" * (3 - self.lives)
        self.canvas.create_text(
            sx(20), sy(45), text=f"Lives: {hearts}", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        self.canvas.create_text(
            sx(20), sy(70), text=f"Level: {self.level}", fill="white",
            font=("Arial", 16, "bold"), anchor="w"
        )
        self.canvas.create_text(
            sx(20), sy(95), text=f"Coins: {self.coins_collected}/{self.coins_needed}",
            fill="#FFD54F", font=("Arial", 16, "bold"), anchor="w"
        )

        # Combo display
        if self.combo > 1:
            combo_text = f"🔥 x{self.combo} COMBO!"
            self.canvas.create_text(
                sx(self.window_width - 20), sy(20), text=combo_text,
                fill="#FFEB3B", font=("Arial", 14, "bold"), anchor="e"
            )

        # Instructions
        self.canvas.create_text(
            sx(self.window_width // 2), sy(20),
            text="Arrow Keys: Move | Space: Jump | R: Restart | Q: Quit",
            fill="white", font=("Arial", 11), anchor="n"
        )

        # Game state overlays
        if self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "win":
            self.draw_win_screen()

    def draw_game_over(self):
        """Draw the game over screen."""
        # Dark overlay
        self.canvas.create_rectangle(
            0, 0, self.window_width, self.window_height,
            fill="black", stipple="gray50"
        )

        # Game over text
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2 - 60,
            text="🐸 GAME OVER 🐸", fill="#FF5252",
            font=("Arial", 48, "bold")
        )
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2,
            text=f"Final Score: {self.score}", fill="white",
            font=("Arial", 28)
        )
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2 + 40,
            text="Press SPACE or R to restart", fill="#B0BEC5",
            font=("Arial", 18)
        )

    def draw_win_screen(self):
        """Draw the victory screen."""
        # Celebration overlay
        self.canvas.create_rectangle(
            0, 0, self.window_width, self.window_height,
            fill="black", stipple="gray50"
        )

        # Win text
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2 - 60,
            text="🎉 YOU WIN! 🎉", fill="#FFD54F",
            font=("Arial", 48, "bold")
        )
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2,
            text=f"Final Score: {self.score}", fill="white",
            font=("Arial", 28)
        )
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2 + 40,
            text="The frog reached the other side!", fill="#69F0AE",
            font=("Arial", 20)
        )
        self.canvas.create_text(
            self.window_width // 2, self.window_height // 2 + 80,
            text="Press SPACE or R to play again", fill="#B0BEC5",
            font=("Arial", 18)
        )

    def restart_game(self):
        """Reset the game to the beginning."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_state = "playing"
        self.coins_collected = 0
        self.coins_needed = 5
        self.combo = 0
        self.combo_timer = 0
        self.screen_shake = 0

        self.frog = Frog(
            self.window_width // 2 - 20,
            self.window_height - 80,
            self.window_width,
            self.window_height
        )
        self.particles = []
        self.generate_level()

    def game_loop(self):
        """Main game loop."""
        if not self.running:
            return

        self.update()
        self.draw()

        self.root.after(16, self.game_loop)  # ~60 FPS

    def run(self):
        """Start the game."""
        self.root.mainloop()


if __name__ == '__main__':
    game = FrogJumpGame()
    game.run()
