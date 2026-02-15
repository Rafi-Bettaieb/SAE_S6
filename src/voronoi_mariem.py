import matplotlib.pyplot as plt
import numpy as np

def lire_fichier(filename):
    points = []
    f = open(filename, 'r')
    for l in f:
        l = l.strip()
        if l:
            x, y = l.split(',')
            points.append([float(x), float(y)])
    f.close()
    return points


def parabola(cord_x, cord_y, ligne, x_values):
    y_values = []
    for x in x_values:
        if abs(cord_y - ligne) < 0.001: 
            y_values.append(cord_y)
        else:
            y = ((x - cord_x)**2 + cord_y**2 - ligne**2) / (2 * (cord_y - ligne))
            y_values.append(y)
    
    return y_values

points = lire_fichier('data/data.txt')
min_x = min(p[0] for p in points) - 2
max_x = max(p[0] for p in points) + 2
min_y = min(p[1] for p in points) - 2
max_y = max(p[1] for p in points) + 2

fig, ax = plt.subplots(figsize=(10, 10))

for p in points:
    ax.plot(p[0], p[1], 'ro', markersize=10)
    ax.text(p[0] + 0.1, p[1] + 0.1, f'({p[0]:.1f},{p[1]:.1f})', fontsize=8)

ligne = 0

ax.axhline(y=ligne, color='blue', linestyle='--', linewidth=2, label='ligne')

x_values = np.linspace(min_x, max_x, 500)

for p in points:
    if p[1] > ligne: 
        y_values = parabola(p[0], p[1], ligne, x_values)
        ax.plot(x_values, y_values, 'g-', linewidth=3, alpha=0.7)

ax.set_xlim(min_x, max_x)
ax.set_ylim(0, max_y) 
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_title('voronoi')
ax.set_xlabel('x')
ax.set_ylabel('y')

plt.tight_layout()
plt.savefig('voronoi_output.png', dpi=150)
plt.show()