# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 12:58:42 2024

@author: JexCher
"""

import math

while True:
    npuntos = int(input("Ingrese el número de puntos (2 - 10): "))
    if 2 <= npuntos <= 10:
        break
    print("Número de puntos fuera de rango. Intente nuevamente.")

puntos = []
for i in range(npuntos):
    while True:
        try:
            x, y = map(int, input(f"Ingrese las coordenadas del punto {chr(65 + i)} (x, y): ").split())
            puntos.append((x, y))
            break
        except ValueError:
            print("Entrada inválida. Intente nuevamente.")

distancias = [[0]*npuntos for K in range(npuntos)]

disminima = float('inf')
p1min, p2min = None, None

for i in range(npuntos):
    for j in range(i + 1, npuntos):
        distancia = math.sqrt((puntos[j][0] - puntos[i][0])**2 + (puntos[j][1] - puntos[i][1])**2)
        distancias[i][j] = distancias[j][i] = distancia
        if distancia < disminima:
            disminima = distancia
            p1min, p2min = i, j

print("\nCuadro de distancias:")
for i in range(npuntos):
    for j in range(npuntos):
        if i != j:
            print(f"Distancia de {chr(65 + i)} a {chr(65 + j)}: {distancias[i][j]:.2f}")
    print()

print(f"La distancia más corta es entre el punto {chr(65 + p1min)} y el punto {chr(65 + p2min)}: {disminima:.2f}")

