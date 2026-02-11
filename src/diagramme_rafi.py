from math import ceil
from random import randint
import sys
from PIL import Image


SCALE_FACTOR = 20

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

palette = {}
for i in range(len(points)):
    palette[i + 1] = {
        "R": randint(0, 255),
        "G": randint(0, 255),
        "B": randint(0, 255)
    }

img = Image.new("RGB", (width, height), "white")

pixels = img.load()
for i in range(width):
    for j in range(height):
        pixel = Screen[i][j]
        if pixel in palette:
            rgb = palette[pixel]
            pixels[i, j] = (rgb["R"], rgb["G"], rgb["B"])

black = (0, 0, 0)
for point in points:
    x = int(point[0])
    y = int(point[1])
    pixels[x, y] = black
         
output_filename = "voronoi_result_rafi.png"
img = img.resize((1024, 1024),Image.NEAREST)
img.save(output_filename)
img.show()


"""
for i in range (width) :
    for j in range (height) :
        print(Screen[i][j], end=" ")
    print()
"""