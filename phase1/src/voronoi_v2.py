from math import ceil
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from collections import deque


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

Screen = [[0 for _ in range(height)] for _ in range(width)]

for i in range (len(points)) :
    x = int(points[i][0])
    y = int(points[i][1])
    Screen[x][y] = i+1

queue = deque()

for i in range(len(points)):
    x = int(points[i][0])
    y = int(points[i][1])
    queue.append((x, y))

while queue:
    x, y = queue.popleft()
    current_owner = Screen[x][y]
    neighbors = [
        (x + 1, y), (x - 1, y),
        (x, y + 1), (x, y - 1),
        (x + 1, y + 1), (x - 1, y - 1),
        (x + 1, y - 1), (x - 1, y + 1)
    ]
    for nx, ny in neighbors:
        if 0 <= nx < width and 0 <= ny < height:
            if Screen[nx][ny] == 0:
                Screen[nx][ny] = current_owner
                queue.append((nx, ny))

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