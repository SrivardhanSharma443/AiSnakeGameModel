import torch
import random
import numpy as np
from collections import deque

from snake import SnakeGameAI, Tile, TILE_SIZE 
from model import Linear_QNet, Qtrainer
from helper import plot
MAX_MEMORY=100_000
BATCH_SIZE=1000
LR=0.001

class Agent:
    def __init__(self):
        self.n_games=0
        self.epsilon=0
        self.gamma=0.9
        self.memory = deque(maxlen=100_000)

        self.model= Linear_QNet(11, 256, 3)
        self.trainer=Qtrainer(self.model, lr=LR, gamma=self.gamma)
    


    def get_state(self, game):
        head = game.snake
        
        point_l = Tile(head.x - TILE_SIZE, head.y)
        point_r = Tile(head.x + TILE_SIZE, head.y)
        point_u = Tile(head.x, head.y - TILE_SIZE)
        point_d = Tile(head.x, head.y + TILE_SIZE)

        dir_l = game.direction == "Left"
        dir_r = game.direction == "Right"
        dir_u = game.direction == "Up"
        dir_d = game.direction == "Down"

        state=[
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            dir_l,
            dir_r,
            dir_u,
            dir_d,

            game.food.x<game.snake.x,
            game.food.x>game.snake.x,
            game.food.y<game.snake.y,
            game.food.y>game.snake.y
        ]
        return np.array(state, dtype=int)
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state , done)

    def train_long_memory(self):
        size=1000
        if len(self.memory)>size:
            mini_batch = random.sample(self.memory, size)
        else:
            mini_batch= self.memory
        states, actions, rewards, next_states, dones = zip(*mini_batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    def get_action(self,state):
        self.epsilon= 80-self.n_games
        final_move=[0, 0, 0]

        if random.randint(0,200)<self.epsilon:
            move=random.randint(0,2)
            final_move[move]=1

        else:
            state0=torch.tensor(state, dtype=torch.float)
            prediction=self.model(state0)
            move=torch.argmax(prediction).item()
            final_move[move]=1
        return final_move
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f'Game {agent.n_games} Score {score} Record {record}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()

