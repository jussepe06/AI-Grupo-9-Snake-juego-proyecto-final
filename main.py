import pygame
import asyncio
from config import *
from entorno import SnakeGame
from telemetria import dibujar_tabla_metricas, exportar_dataset

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Autonomo - IA Modular")
    clock = pygame.time.Clock()
    
    font_title = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 18)
    
    modos = ["aleatorio", "bfs", "astar"]
    N_partidas = 3 
    resultados = {}
    
    print("Fase de simulacion automatica en progreso...")
    
    for modo in modos:
        game = SnakeGame(mode=modo)
        while game.metrics["games_played"] < N_partidas:
            game.step()
            if game.game_over:
                game.reset()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exportar_dataset()
                    pygame.quit()
                    return
            await asyncio.sleep(0)
            
        steps = max(1, game.metrics["total_steps"])
        avg_nodes = game.metrics["total_nodes_expanded"] / steps
        avg_time = game.metrics["total_inference_time"] / steps
        win_rate = (game.metrics["wins"] / N_partidas) * 100
        
        resultados[modo] = {
            "max_len": game.metrics["max_length"],
            "win_rate": win_rate,
            "avg_nodes": avg_nodes,
            "avg_time": avg_time
        }

    # Fase 1: Mostrar tabla renderizada en Pygame
    showing_table = True
    while showing_table:
        dibujar_tabla_metricas(screen, font_title, font_small, resultados, modos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exportar_dataset()
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    showing_table = False
        await asyncio.sleep(0)

    # Fase Demo Interactiva
    idx_modo = 2
    game = SnakeGame(mode=modos[idx_modo])
    manual_control = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    manual_control = not manual_control
                    if manual_control:
                        game.mode = "manual"
                    else:
                        game.mode = modos[idx_modo]
                elif event.key == pygame.K_SPACE:
                    idx_modo = (idx_modo + 1) % len(modos)
                    if not manual_control:
                        game.mode = modos[idx_modo]
                
                if manual_control:
                    if event.key == pygame.K_UP and game.direction != DOWN:
                        game.direction = UP
                    elif event.key == pygame.K_DOWN and game.direction != UP:
                        game.direction = DOWN
                    elif event.key == pygame.K_LEFT and game.direction != RIGHT:
                        game.direction = LEFT
                    elif event.key == pygame.K_RIGHT and game.direction != LEFT:
                        game.direction = RIGHT
                        
        if not manual_control:
            game.step()
        else:
            head = game.snake[0]
            new_head = (head[0] + game.direction[0], head[1] + game.direction[1])
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in game.snake):
                game.reset()
            else:
                game.snake.insert(0, new_head)
                if new_head == game.apple:
                    game.score += 1
                    game.apple = game._spawn_apple()
                else:
                    game.snake.pop()
            
        if game.game_over:
            game.reset()
            
        screen.fill(BLACK)
        for segment in game.snake:
            pygame.draw.rect(screen, GREEN, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, (game.apple[0]*CELL_SIZE, game.apple[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        modo_actual = "Manual" if manual_control else game.mode.upper()
        texto_modo = font_small.render(f"Modo: {modo_actual} (Espacio para cambiar)", True, WHITE)
        texto_score = font_small.render(f"Puntaje: {game.score}", True, WHITE)
        
        screen.blit(texto_modo, (10, 10))
        screen.blit(texto_score, (10, 30))
        
        pygame.display.flip()
        clock.tick(15) 
        
        await asyncio.sleep(0) 
        
    exportar_dataset()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
