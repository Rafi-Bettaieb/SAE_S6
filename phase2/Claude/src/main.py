"""
main.py
-------
Point d'entrée de l'application de diagramme de Voronoï.

Usage :
    python main.py

Modules :
    voronoi_calc.py  → Algorithme de calcul (Bowyer-Watson + Delaunay dual)
    voronoi_svg.py   → Export SVG
    voronoi_gui.py   → Interface graphique Tkinter
"""

import sys
import time

start = time.time()


def main():
    """Lance l'application graphique."""
    try:
        from voronoi_gui import VoronoiApp
    except ImportError as e:
        print(f"Erreur d'import : {e}")
        print("Assurez-vous que tkinter est installé.")
        sys.exit(1)

    app = VoronoiApp()
    app.mainloop()


end = time.time()

print("Temps :", end - start)

if __name__ == "__main__":
    main()
    

