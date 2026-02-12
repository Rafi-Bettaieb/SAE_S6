import numpy as np
import math
import matplotlib.pyplot as plt

#extraction des points du fichier data.txt

f = open("./data/data.txt", "r")

lines = f.readlines()

points_list = []

for line in lines:
    line = line.strip()
    parts = line.split(",")

    x = float(parts[0])
    y = float(parts[1])

    points_list.append([x, y])

f.close()
points = np.array(points_list)
print(points)
