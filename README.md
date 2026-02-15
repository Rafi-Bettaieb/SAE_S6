# SAE S6 : Diagrammes de Voronoï

Ce projet est une application Python permettant de générer et visualiser des diagrammes de Voronoï à partir d'une liste de points (coordonnées 2D).

# Phase 1
##  Fonctionnalités 
- Importation de fichiers de points (format `.txt`).
- Calcul et affichage du diagramme de Voronoï.
- Exportation du résultat (Image et/ou SVG).

## Installation

1. Clonez ce dépôt :
   avec HTTPS :
   ```bash
   git clone https://github.com/Rafi-Bettaieb/SAE_S6.git
   ```
   avec SSH :
   ```bash
   git clone git@github.com:Rafi-Bettaieb/SAE_S6.git
   ```

2. je vais implementer l'algorithme de delaunay (Bowyer-Watson) puis transformer ce graph en voronoi.

j'ai decouvert d'apres cette resource:
https://www.youtube.com/watch?v=ysLCuqcyJZA qu'il y a une relation de dualité entre la triangularité de delauney et le diagramme de voronoi.
j'ai trouvé que c'est plus simple de calculer d'abord les triangulation de delauney puis les convertir en diagramme de voronoi car c'est facile a comprendre.
tout d'abord il faut parcourir chaque triplet de points et voir si il y a aucun point a l'interieur du cercle circonscrit ce qui si c'est le cas est un triangle valide sinon ce n'est pas une triangulation valide. ensuite le centre de chaque triangle valide selon l'algorithme de delauney formé par le centre du cercle circonscrit de ce triangle est en fait un point critique pour le diagramme de voronoi nommé "vertex". ce vertex est un point d'intersection des bords du diagramme de voronoi. donc maintenant qu'on a tout les point nommé "vertex" il suffit juste de les relier entre eux mais selon une methode specifique et pas n'importe comment. si deux triangles partage un meme coté, on relie leurs centres. (probleme les points exterieurs.) solution, detecter les bords des triangles qui appartiennent a un seul triangle et qui n'est pas partagé avec d'autres triangles ensuite on trace une droite perpendiculaire a celle ci  et on la relie avec le centre le plus proche et le bord de l'image.
