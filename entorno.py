import random
from config import *
from agentes import get_random_action, get_bfs_action, get_astar_action, extract_features
from telemetria import registrar_estado

class SnakeGame:
    def __init__(self, mode="aleatorio"):
        self.mode = mode
        self.metrics = {
            "max_length": 0,
            "wins": 0,
            "total_nodes_expanded": 0,
            "total_steps": 0,
            "total_inference_time": 0.0,
            "games_played": 0
        }
        self.reset()

    def reset(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.apple = self._spawn_apple()
        self.game_over = False
        self.score = 0

    def _spawn_apple(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def step(self):
        if self.game_over:
            return
            
        nodes = 0
        inference_time = 0.0
        
        if self.mode == "aleatorio":
            action, nodes, inference_time = get_random_action(self.snake)
        elif self.mode == "bfs":
            action, nodes, inference_time = get_bfs_action(self.snake, self.apple)
        elif self.mode == "astar":
            action, nodes, inference_time = get_astar_action(self.snake, self.apple)
            
            # Fase 3: Registro de features
            features = extract_features(self.snake, self.apple)
            map_actions = {UP: "ARRIBA", DOWN: "ABAJO", LEFT: "IZQUIERDA", RIGHT: "DERECHA"}
            action_label = map_actions.get(action, "DESCONOCIDO")
            registrar_estado(features, action_label)
        else:
            action = self.direction
            
        # Evitar reverso
        if len(self.snake) > 1:
            if (action[0] == -self.direction[0] and action[1] == -self.direction[1]):
                action = self.direction
                
        self.direction = action
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Validar Colisiones
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            self.metrics["games_played"] += 1
            if len(self.snake) > self.metrics["max_length"]:
                self.metrics["max_length"] = len(self.snake)
            if len(self.snake) >= 20: 
                self.metrics["wins"] += 1
            return
            
        self.snake.insert(0, new_head)
        
        # Actualizar Metricas
        self.metrics["total_nodes_expanded"] += nodes
        self.metrics["total_inference_time"] += inference_time
        self.metrics["total_steps"] += 1
        
        # Logica Manzana
        if new_head == self.apple:
            self.score += 1
            if len(self.snake) < GRID_WIDTH * GRID_HEIGHT:
                self.apple = self._spawn_apple()
            else:
                self.game_over = True
                self.metrics["games_played"] += 1
                self.metrics["wins"] += 1
                if len(self.snake) > self.metrics["max_length"]:
                    self.metrics["max_length"] = len(self.snake)
        else:
            self.snake.pop()
