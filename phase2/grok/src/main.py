import sys
import os
import tkinter as tk

chemin_racine = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

if chemin_racine not in sys.path:
    sys.path.insert(0, chemin_racine)

from phase2.grok.src.gui import VoronoiApp

if __name__ == "__main__":
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()