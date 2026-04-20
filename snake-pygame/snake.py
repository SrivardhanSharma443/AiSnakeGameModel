import tkinter
import random
import numpy as np
import time

ROWS = 25
COLS = 25
TILE_SIZE = 25
WINDOW_WIDTH = TILE_SIZE * COLS
WINDOW_HEIGHT = TILE_SIZE * ROWS

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class SnakeGameAI:
    def __init__(self):
        self.window= tkinter.Tk()
        self.window.title("Snake Ai")
        self.window.resizable(False, False)

        self.canvas= tkinter.Canvas(self.window, bg="Black", width= WINDOW_WIDTH, height= WINDOW_HEIGHT, borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        #Keeps the window Open
        self.running= True
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.reset()
    def on_close(self):
        self.running= False
        self.window.destroy()
    def reset(self):
        self.snake=Tile(5*TILE_SIZE, 5*TILE_SIZE)
        self.food= Tile(10*TILE_SIZE, 10*TILE_SIZE)
        self.snake_body=[]
        self.velocityX=0
        self.velocityY=0
        self.game_over=False
        self.score=0
        self.direction="Right"
        self.frame_iteration=0
    def play_step(self, action):
        self.frame_iteration+=1

        self.window.update_idletasks()
        self.window.update()
        #time.sleep(nosleep)

        self._move(action)
        self.snake.x+= self.velocityX*TILE_SIZE
        self.snake.y += self.velocityY*TILE_SIZE

        reward=0
        game_over=False

        if self.is_collision() or self.frame_iteration>100*(len(self.snake_body)+1):
            game_over=True
            reward=-10
            return reward, game_over,self.score
        for i in range(len(self.snake_body)-1, -1, -1):
            tile = self.snake_body[i]
            if i == 0:
                tile.x = self.snake.x - self.velocityX * TILE_SIZE # Undo head move to get previous spot
                tile.y = self.snake.y - self.velocityY * TILE_SIZE
            else:
                prev_tile = self.snake_body[i-1]
                tile.x = prev_tile.x
                tile.y = prev_tile.y

        # 5. Check Food
        if (self.snake.x == self.food.x and self.snake.y == self.food.y):
            self.score += 1
            reward = 10
            self.snake_body.append(Tile(self.snake.x, self.snake.y)) # Add new tail
            self._place_food()
            self.frame_iteration = 0 # Reset starvation timer
            
        # 6. Draw
        self._draw_ui()
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt= self.snake
        if pt.x < 0 or pt.x >= WINDOW_WIDTH or pt.y < 0 or pt.y >= WINDOW_HEIGHT:
            return True
        # Hits itself
        for tile in self.snake_body:
            if pt.x == tile.x and pt.y == tile.y:
                return True
        return False
    def _place_food(self):
        while True:
            new_x = random.randint(0, COLS-1) * TILE_SIZE
            new_y = random.randint(0, ROWS-1) * TILE_SIZE
            on_snake = any(tile.x == new_x and tile.y == new_y for tile in self.snake_body)
            if (new_x != self.snake.x or new_y != self.snake.y) and not on_snake:
                self.food.x = new_x
                self.food.y = new_y
                break
    def _move(self, action):
        clock_wise = ["Right", "Down", "Left", "Up"]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] 
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] 
        else: 
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]
        self.direction= new_dir

        if self.direction == "Right":
            self.velocityX = 1
            self.velocityY = 0
        elif self.direction == "Left":
            self.velocityX = -1
            self.velocityY = 0
        elif self.direction == "Down":
            self.velocityX = 0
            self.velocityY = 1
        elif self.direction == "Up":
            self.velocityX = 0
            self.velocityY = -1

      
    
    def _draw_ui(self):
        self.canvas.delete("all")
        
        # Draw Food
        self.canvas.create_rectangle(self.food.x, self.food.y, self.food.x + TILE_SIZE, self.food.y + TILE_SIZE, fill="red")
        
        # Draw Snake
        self.canvas.create_rectangle(self.snake.x, self.snake.y, self.snake.x + TILE_SIZE, self.snake.y + TILE_SIZE, fill="green")
        for tile in self.snake_body:
            canvas_tile = self.canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE, fill="green")
        
        # Draw Score
        self.canvas.create_text(35, 20, font="Arial 10", text=f"Score: {self.score}", fill="white")
        
        if self.game_over:
            self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, font="Arial 20", text=f"Game Over: {self.score}", fill="white")
    

if __name__ == '__main__':
    game = SnakeGameAI()
    

    while True:

        action = [0, 0, 0]
        action[random.randint(0, 2)] = 1
        

        reward, game_over, score = game.play_step(action)
        
        if game_over:
            game.reset()
