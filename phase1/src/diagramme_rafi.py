from math import ceil
from random import randint
import sys
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np


SCALE_FACTOR = 10

with open("data/data.txt", "r") as f:
    content = f.read()  
    liste = content.split() 
    points = []
    for i in range(len(liste)) :
        x,y = liste[i].split(",")
        points.append((float(x) * SCALE_FACTOR, float(y) * SCALE_FACTOR))

max_abscisse = 0
max_ordonnee = 0

for i in range(len(points)) :
    max_abscisse = max(max_abscisse, points[i][0])
    max_ordonnee = max(max_ordonnee, points[i][1])

height = ceil(max_ordonnee) + (30)
width = ceil(max_abscisse) + (30)

"""
Screen = [[]]
for i in range (width) :
    for j in range (height) :
        Screen[i][j] = 0
"""
Screen = [[0 for _ in range(height)] for _ in range(width)]

for i in range (len(points)) :
    x = int(points[i][0])
    y = int(points[i][1])
    Screen[x][y] = i+1

for i in range (width) :
    for j in range (height) :
        if(Screen[i][j] != 0):
            continue
        dist = sys.maxsize
        meilleur_index = 0
        for k in range (len(points)) :
            point = points[k]
            x = point[0]
            y = point[1]
            current_dist = (x - i) ** 2 + (y - j) ** 2
            if(current_dist < dist) :
                Screen[i][j] = k + 1
                dist = current_dist

"""
for i in range (width) :
    for j in range (height) :
        print(Screen[i][j], end=" ")
    print()
"""

colors = np.random.rand(len(points) + 1, 3)

grid_array = np.array(Screen).T

output_image = colors[grid_array]

plt.figure(figsize=(10, 10))
plt.imshow(output_image)

x = [p[0] for p in points]
y = [p[1] for p in points]

plt.scatter(x, y, c='black', marker='x' , label='cellule')
plt.title("Diagramme de Voronoi")
plt.axis('off')
plt.legend()
plt.show()