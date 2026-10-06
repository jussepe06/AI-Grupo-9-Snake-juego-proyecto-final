import random
import time
import heapq
from collections import deque
from config import *

def extract_features(snake, apple):
    head = snake[0]
    dist_x_norm = (apple[0] - head[0]) / GRID_WIDTH
    dist_y_norm = (apple[1] - head[1]) / GRID_HEIGHT
    
    def check_danger(dx, dy):
        nx, ny = head[0] + dx, head[1] + dy
        if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT or (nx, ny) in snake:
            return 1
        return 0
        
    danger_up = check_danger(0, -1)
    danger_down = check_danger(0, 1)
    danger_left = check_danger(-1, 0)
    danger_right = check_danger(1, 0)
    
    return [dist_x_norm, dist_y_norm, danger_up, danger_down, danger_left, danger_right]

def get_random_action(snake):
    start_time = time.perf_counter()
    head = snake[0]
    valid_moves = []
    for dx, dy in DIRECTIONS:
        nx, ny = head[0] + dx, head[1] + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and (nx, ny) not in snake:
            valid_moves.append((dx, dy))
    
    action = random.choice(valid_moves) if valid_moves else random.choice(DIRECTIONS)
    inference_time = (time.perf_counter() - start_time) * 1000
    return action, 0, inference_time

def get_bfs_action(snake, apple):
    start_time = time.perf_counter()
    head = snake[0]
    queue = deque([(head, [])])
    visited = {head}
    nodes_expanded = 0
    body_set = set(snake)
    path = None
    
    while queue:
        current, current_path = queue.popleft()
        nodes_expanded += 1
        if current == apple:
            path = current_path
            break
        for dx, dy in DIRECTIONS:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if neighbor not in body_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, current_path + [(dx, dy)]))
                    
    inference_time = (time.perf_counter() - start_time) * 1000
    if path:
        return path[0], nodes_expanded, inference_time
    
    # Fallback
    action, _, _ = get_random_action(snake)
    return action, nodes_expanded, inference_time

def flood_fill_count(start, body_set, limit):
    queue = deque([start])
    visited = {start}
    count = 0
    while queue and count < limit:
        curr = queue.popleft()
        count += 1
        for dx, dy in DIRECTIONS:
            nx, ny = curr[0] + dx, curr[1] + dy
            neighbor = (nx, ny)
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if neighbor not in body_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return count

def get_astar_action(snake, apple):
    start_time = time.perf_counter()
    head = snake[0]
    body_set = set(snake)
    open_set = []
    iter_counter = 0 
    heapq.heappush(open_set, (0, 0, iter_counter, head, []))
    g_scores = {head: 0}
    nodes_expanded = 0
    path = None
    target_length = len(snake)
    
    while open_set:
        _, g, _, current, current_path = heapq.heappop(open_set)
        nodes_expanded += 1
        if current == apple:
            path = current_path
            break
        for dx, dy in DIRECTIONS:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if neighbor not in body_set:
                    tentative_g = g + 1
                    if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                        g_scores[neighbor] = tentative_g
                        h = abs(neighbor[0] - apple[0]) + abs(neighbor[1] - apple[1])
                        # Penalizacion en raiz
                        if len(current_path) == 0:
                            reachable = flood_fill_count(neighbor, body_set, target_length)
                            if reachable < target_length:
                                h += 10000 
                        f = tentative_g + h
                        iter_counter += 1
                        heapq.heappush(open_set, (f, tentative_g, iter_counter, neighbor, current_path + [(dx, dy)]))
                        
    inference_time = (time.perf_counter() - start_time) * 1000
    
    if path:
        return path[0], nodes_expanded, inference_time
        
    action, _, _ = get_random_action(snake)
    return action, nodes_expanded, inference_time
