import pygame
import sys
import csv
from config import *

# Variable global para el dataset de Machine Learning
global_dataset = []

def registrar_estado(features, action):
    global global_dataset
    global_dataset.append(features + [action])

def dibujar_tabla_metricas(pantalla, font_title, font_small, resultados, modos):
    pantalla.fill(BLACK)
    
    titulo = font_title.render("Tabla de Resultados", True, WHITE)
    pantalla.blit(titulo, (10, 20))
    
    headers = ["Tecnica", "Max", "Win%", "Nodos/J", "Ms/Jug"]
    x_offsets = [10, 100, 160, 230, 320]
    
    # Dibujar headers
    for i, h in enumerate(headers):
        text = font_small.render(h, True, GREEN)
        pantalla.blit(text, (x_offsets[i], 60))
        
    y = 90
    for modo in modos:
        res = resultados[modo]
        nodos_str = f"{res['avg_nodes']:.1f}" if modo != "aleatorio" else "N/A"
        
        row_data = [
            modo.upper(),
            str(res['max_len']),
            f"{res['win_rate']:.1f}%",
            nodos_str,
            f"{res['avg_time']:.4f}"
        ]
        
        for i, data in enumerate(row_data):
            text = font_small.render(data, True, WHITE)
            pantalla.blit(text, (x_offsets[i], y))
            
        y += 40
        
    instruccion = font_small.render("Presiona ESPACIO para continuar al juego interactivo...", True, RED)
    pantalla.blit(instruccion, (10, HEIGHT - 30))
    pygame.display.flip()

def exportar_dataset():
    # Solo guardamos si no estamos en web (emscripten)
    if sys.platform != "emscripten":
        if len(global_dataset) > 0:
            try:
                with open("dataset_snake.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["dist_x", "dist_y", "danger_up", "danger_down", "danger_left", "danger_right", "action"])
                    writer.writerows(global_dataset)
                print(f"Dataset exportado exitosamente: dataset_snake.csv ({len(global_dataset)} registros).")
            except Exception as e:
                print(f"Error al exportar dataset: {e}")
