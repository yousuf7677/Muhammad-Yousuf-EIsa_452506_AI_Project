import tkinter as tk
import random
import time

class DifficultySelection:
    def __init__(self, master):
        self.master = master
        self.master.title("Snake Game - Difficulty Selection")
        self.master.geometry("300x150")
        self.master.resizable(False, False)

        self.label = tk.Label(self.master, text="Select Difficulty:")
        self.label.pack(pady=10)

        self.difficulty_var = tk.StringVar()
        self.difficulty_var.set("medium")

        difficulty_levels = ["easy", "medium", "hard"]
        for level in difficulty_levels:
            radio_button = tk.Radiobutton(self.master, text=level.capitalize(), variable=self.difficulty_var, value=level)
            radio_button.pack()

        self.start_button = tk.Button(self.master, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)

    def start_game(self):
        self.master.destroy()
        difficulty = self.difficulty_var.get()
        root = tk.Tk()
        game = SnakeGame(root, difficulty)
        root.mainloop()

class SnakeGame:
    def __init__(self, master, difficulty):
        self.master = master
        self.master.title("Snake Game")
        self.master.geometry("400x400")
        self.master.resizable(False, False)

        self.canvas = tk.Canvas(self.master, bg="lightblue", width=400, height=400)
        self.canvas.pack()

        self.snake = [(100, 100), (90, 100), (80, 100)]
        self.enemy_snake = [(300, 300), (310, 300), (320, 300)]  # Initial positions for the enemy snake
        self.direction = "Right"
        self.enemy_direction = "Left"  # Initial direction for the enemy snake
        self.score = 0
        self.enemy_score = 0

        self.food = None
        self.obstacles = self.create_obstacles(difficulty)

        self.master.bind("<KeyPress>", self.change_direction)

        self.game_over_flag = False
        self.time_limit = 60  # 60 seconds time limit
        self.start_time = time.time()
        self.update()

    def create_food(self):
        if not self.food:
            x = random.randint(0, 19) * 20
            y = random.randint(0, 19) * 20
            self.food = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="red")

    def create_obstacles(self, difficulty):
        obstacles = []
        if difficulty != "easy":
            for _ in range(3):
                x = random.randint(0, 19) * 20
                y = random.randint(0, 19) * 20
                obstacle = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="blue")
                obstacles.append(obstacle)
        return obstacles

    def move_snake(self):
        if self.game_over_flag:
            return

        head = self.snake[0]
        if self.direction == "Right":
            new_head = (head[0] + 20, head[1])
        elif self.direction == "Left":
            new_head = (head[0] - 20, head[1])
        elif self.direction == "Up":
            new_head = (head[0], head[1] - 20)
        elif self.direction == "Down":
            new_head = (head[0], head[1] + 20)

        if not self.check_collision(new_head):
            self.snake.insert(0, new_head)
            self.snake.pop()
        else:
            self.game_over()

    def move_enemy_snake(self):
        if self.game_over_flag:
            return

        head = self.enemy_snake[0]

        # If food is present, make the enemy snake move towards the food
        if self.food:
            food_coords = self.canvas.coords(self.food)
            if head[0] < food_coords[0]:
                self.enemy_direction = "Right"
            elif head[0] > food_coords[0]:
                self.enemy_direction = "Left"
            elif head[1] < food_coords[1]:
                self.enemy_direction = "Down"
            elif head[1] > food_coords[1]:
                self.enemy_direction = "Up"

        new_head = None

        # Ensure the enemy snake doesn't hit the boundary
        while True:
            if self.enemy_direction == "Right":
                new_head = (head[0] + 20, head[1])
            elif self.enemy_direction == "Left":
                new_head = (head[0] - 20, head[1])
            elif self.enemy_direction == "Up":
                new_head = (head[0], head[1] - 20)
            elif self.enemy_direction == "Down":
                new_head = (head[0], head[1] + 20)

            if not self.check_collision(new_head, enemy=True):
                break
            else:
                self.enemy_direction = random.choice(["Right", "Left", "Up", "Down"])

        self.enemy_snake.insert(0, new_head)
        self.enemy_snake.pop()

    def check_collision(self, position, enemy=False):
        if position[0] < 0 or position[0] >= 400 or position[1] < 0 or position[1] >= 400:
            return True

        for obstacle in self.obstacles:
            obstacle_coords = self.canvas.coords(obstacle)
            if position[0] == obstacle_coords[0] and position[1] == obstacle_coords[1]:
                return True

        if not enemy and position in self.enemy_snake:
            return True
        elif enemy and position in self.snake:
            return True

        return False

    def update(self):
        self.move_snake()
        self.move_enemy_snake()

        head = self.snake[0]
        head_enemy = self.enemy_snake[0]

        self.canvas.delete("snake")
        for segment in self.snake:
            self.canvas.create_rectangle(segment[0], segment[1], segment[0] + 20, segment[1] + 20, fill="green", tags="snake")

        self.canvas.delete("enemy_snake")
        for segment in self.enemy_snake:
            self.canvas.create_rectangle(segment[0], segment[1], segment[0] + 20, segment[1] + 20, fill="orange", tags="enemy_snake")

        self.create_food()

        if self.food:
            food_coords = self.canvas.coords(self.food)
            if head[0] == food_coords[0] and head[1] == food_coords[1]:
                self.snake.append((0, 0))
                self.canvas.delete(self.food)
                self.food = None
                self.score += 1

            # Check if the enemy snake has reached the food
            if head_enemy[0] == food_coords[0] and head_enemy[1] == food_coords[1]:
                self.enemy_snake.append((0, 0))
                self.canvas.delete(self.food)
                self.food = None
                self.enemy_score += 1

        self.show_score()

        elapsed_time = int(time.time() - self.start_time)
        remaining_time = max(0, self.time_limit - elapsed_time)
        if not self.game_over_flag and remaining_time > 0:
            if self.score >= 10 or self.enemy_score >= 10:
                self.game_over()
            else:
                self.master.after(200, self.update)
        else:
            self.game_over()

    def change_direction(self, event):
        if event.keysym == "Right" and not self.direction == "Left":
            self.direction = "Right"
        elif event.keysym == "Left" and not self.direction == "Right":
            self.direction = "Left"
        elif event.keysym == "Up" and not self.direction == "Down":
            self.direction = "Up"
        elif event.keysym == "Down" and not self.direction == "Up":
            self.direction = "Down"

    def game_over(self):
        if not self.game_over_flag:
            winner_text = ""
            if self.score > self.enemy_score:
                winner_text = "Congratulations! You Win!"
            elif self.score < self.enemy_score:
                winner_text = "Sorry! AI Wins!"
            else:
                winner_text = "It's a Tie!"

            # Display the game over screen
            self.canvas.create_rectangle(0, 0, 400, 400, fill="black", tags="game_over")
            self.canvas.create_text(200, 200, text="Game Over!", fill="red", font=("Helvetica", 16), tags="game_over")
            self.canvas.create_text(200, 220, text=winner_text, fill="red", font=("Helvetica", 16), tags="game_over")

            self.game_over_flag = True

    def show_score(self):
        # Clear previous score text
        self.canvas.delete("score_text")
        self.canvas.delete("time_text")

        score_color = "black" if not self.game_over_flag else "white"
        time_color = "black" if not self.game_over_flag else "white"

        score_text = f"Your Score: {self.score}, AI Score: {self.enemy_score}"
        self.canvas.create_text(200, 70, text=score_text, fill=score_color, font=("Helvetica", 12), anchor="w", tags="score_text")

        time_text = f"Time Left: {max(0, self.time_limit - int(time.time() - self.start_time))}s"
        self.canvas.create_text(200, 50, text=time_text, fill=time_color, font=("Helvetica", 12), anchor="w", tags="time_text")

if __name__ == "__main__":
    root = tk.Tk()
    difficulty_selector = DifficultySelection(root)
    root.mainloop()



