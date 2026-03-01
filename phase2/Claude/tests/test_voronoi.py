"""
test_voronoi.py
---------------
Tests pour le diagramme de Voronoï.
Lancement : pytest test_voronoi.py -v
"""

import math
import os
import re
import pytest

from voronoi_calc import (
    Point, Triangle, VoronoiDiagram,
    bowyer_watson, compute_voronoi, load_points_from_file,
    _sorted_edge,
)
from voronoi_svg import export_to_svg


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def diagram():
    pts = [Point(0,0), Point(10,0), Point(5,10), Point(2,5), Point(8,5)]
    return compute_voronoi(pts)

@pytest.fixture
def svg_file(tmp_path):
    return str(tmp_path / "voronoi.svg")

@pytest.fixture
def points_file(tmp_path):
    f = tmp_path / "points.txt"
    f.write_text("# commentaire\n1.0, 2.0\n3.0, 4.0\n5.0, 6.0\n")
    return str(f)

@pytest.fixture
def small_pts_diagram():
    pts = [Point(0,0), Point(20,0), Point(10,15), Point(5,10), Point(15,10)]
    return compute_voronoi(pts)

def _site_circles(svg_path):
    content = open(svg_path, encoding="utf-8").read()
    return [(float(cx), float(cy))
            for cx, cy in re.findall(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="4\.0"', content)]


# =============================================================================
# Point
# =============================================================================

def test_should_store_coordinates_and_compute_distance_correctly():
    # Arrange
    p1, p2 = Point(0, 0), Point(3, 4)
    # Act & Assert
    assert p1.x == 0 and p1.y == 0
    assert p1.distance_to(p2) == pytest.approx(5.0)

def test_should_support_arithmetic_operations():
    # Arrange
    a, b = Point(1, 2), Point(3, 4)
    # Act & Assert
    assert a + b == Point(4, 6)
    assert b - a == Point(2, 2)
    assert a * 3 == Point(3, 6)

def test_should_be_immutable_and_hashable():
    # Arrange
    p = Point(1.0, 2.0)
    # Act & Assert
    with pytest.raises((AttributeError, TypeError)):
        p.x = 99.0
    assert len({p, Point(1.0, 2.0), Point(3.0, 4.0)}) == 2


# =============================================================================
# Triangle
# =============================================================================

def test_should_compute_circumcenter_equidistant_from_vertices():
    # Arrange
    t = Triangle(Point(0,0), Point(3,0), Point(0,4))
    cc = t.circumcenter
    # Act & Assert
    assert cc is not None
    assert cc.distance_to(t.a) == pytest.approx(cc.distance_to(t.b), abs=1e-6)
    assert cc.distance_to(t.b) == pytest.approx(cc.distance_to(t.c), abs=1e-6)

def test_should_detect_point_inside_and_outside_circumcircle():
    # Arrange
    h = math.sqrt(3)
    t = Triangle(Point(-1,0), Point(1,0), Point(0,h))
    # Act & Assert
    assert t.point_in_circumcircle(Point(0, 0.3)) is True
    assert t.point_in_circumcircle(Point(100, 100)) is False

def test_should_return_none_circumcenter_given_collinear_points():
    # Arrange & Act
    t = Triangle(Point(0,0), Point(1,0), Point(2,0))
    # Assert
    assert t.circumcenter is None

def test_should_detect_shared_edge_between_adjacent_triangles():
    # Arrange
    a, b = Point(0,0), Point(1,0)
    t1 = Triangle(a, b, Point(0.5,  1))
    t2 = Triangle(a, b, Point(0.5, -1))
    t3 = Triangle(Point(5,5), Point(6,5), Point(5.5,6))
    # Act & Assert
    assert t1.shares_edge_with(t2) is True
    assert t1.shares_edge_with(t3) is False


# =============================================================================
# bowyer_watson
# =============================================================================

def test_should_raise_error_given_less_than_3_points():
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        bowyer_watson([Point(0,0), Point(1,1)])

def test_should_return_correct_triangle_count_given_simple_inputs():
    # Arrange
    pts3 = [Point(0,0), Point(1,0), Point(0.5,1)]
    pts4 = [Point(0,0), Point(1,0), Point(1,1), Point(0,1)]
    # Act & Assert
    assert len(bowyer_watson(pts3)) == 1
    assert len(bowyer_watson(pts4)) == 2

def test_should_satisfy_delaunay_property():
    # Arrange
    pts = [Point(0,0), Point(3,0), Point(6,0),
           Point(1,2), Point(4,2), Point(2,4)]
    # Act
    triangles = bowyer_watson(pts)
    # Assert: aucun point dans le cercle circonscrit d'un triangle
    for t in triangles:
        for p in pts:
            if p not in (t.a, t.b, t.c):
                assert t.point_in_circumcircle(p) is False

def test_should_include_all_input_points_as_vertices():
    # Arrange
    pts = [Point(0,0), Point(4,0), Point(2,3), Point(1,1), Point(3,1)]
    # Act
    triangles = bowyer_watson(pts)
    vertices = {v for t in triangles for v in (t.a, t.b, t.c)}
    # Assert
    for p in pts:
        assert p in vertices


# =============================================================================
# compute_voronoi
# =============================================================================

def test_should_return_valid_diagram_with_sites_and_edges(diagram):
    # Arrange & Act & Assert
    assert isinstance(diagram, VoronoiDiagram)
    assert len(diagram.sites) == 5
    assert len(diagram.edges) > 0

def test_should_contain_all_sites_within_bounds(diagram):
    # Arrange
    x_min, y_min, x_max, y_max = diagram.bounds
    # Act & Assert
    for p in diagram.sites:
        assert x_min <= p.x <= x_max
        assert y_min <= p.y <= y_max

def test_should_produce_non_degenerate_edges(diagram):
    # Arrange & Act & Assert
    for p1, p2 in diagram.edges:
        assert p1.distance_to(p2) > 1e-6

def test_should_return_perpendicular_bisector_given_two_points():
    # Arrange
    diag = compute_voronoi([Point(0,0), Point(4,0)])
    a, b = diag.edges[0]
    # Act & Assert
    assert len(diag.edges) == 1
    assert a.x == pytest.approx(b.x, abs=1e-3)   # droite verticale
    assert a.x == pytest.approx(2.0, abs=1e-3)    # passe par le milieu

def test_should_raise_error_given_invalid_inputs():
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        compute_voronoi([])
    with pytest.raises(ValueError):
        compute_voronoi([Point(0,0)])
    with pytest.raises(ValueError):
        compute_voronoi([Point(1,1), Point(1,1), Point(1,1)])

def test_should_deduplicate_points_and_give_same_result_twice():
    # Arrange
    pts = [Point(0,0), Point(5,0), Point(2.5,5)]
    # Act
    d1 = compute_voronoi(pts + [pts[0]])
    d2 = compute_voronoi(pts)
    # Assert
    assert len(d1.sites) == len(d2.sites) == 3
    assert len(d1.edges) == len(d2.edges)


# =============================================================================
# load_points_from_file
# =============================================================================

def test_should_parse_valid_points_and_ignore_comments(points_file):
    # Arrange & Act
    pts = load_points_from_file(points_file)
    # Assert
    assert len(pts) == 3
    assert pts[0] == Point(1.0, 2.0)
    assert pts[2] == Point(5.0, 6.0)

def test_should_parse_comma_and_space_separators(tmp_path):
    # Arrange
    f = tmp_path / "p.txt"
    f.write_text("1 2\n3,4\n5 6\n")
    # Act
    pts = load_points_from_file(str(f))
    # Assert
    assert pts == [Point(1,2), Point(3,4), Point(5,6)]

def test_should_raise_error_given_invalid_file(tmp_path):
    # Arrange
    f_one  = tmp_path / "one.txt"
    f_bad  = tmp_path / "bad.txt"
    f_one.write_text("1 2\n")
    f_bad.write_text("1 2\n42\n3 4\n")
    # Act & Assert
    with pytest.raises(ValueError):
        load_points_from_file(str(f_one))   # un seul point
    with pytest.raises(ValueError):
        load_points_from_file(str(f_bad))   # ligne malformée
    with pytest.raises(FileNotFoundError):
        load_points_from_file("/tmp/inexistant_xyz.txt")


# =============================================================================
# export_to_svg
# =============================================================================

def test_should_create_valid_svg_file_with_correct_dimensions(diagram, svg_file):
    # Arrange & Act
    import xml.etree.ElementTree as ET
    export_to_svg(diagram, svg_file, width=1024, height=768)
    root = ET.parse(svg_file).getroot()
    # Assert
    assert os.path.getsize(svg_file) > 0
    assert "svg" in root.tag
    assert root.get("width") == "1024"
    assert root.get("height") == "768"

def test_should_contain_lines_circles_and_labels(diagram, svg_file):
    # Arrange & Act
    export_to_svg(diagram, svg_file, show_labels=True)
    content = open(svg_file, encoding="utf-8").read()
    # Assert
    assert "<line"   in content
    assert "<circle" in content
    assert "<text"   in content


# =============================================================================
# Repère écran (Y vers le bas) + Zoom automatique
# =============================================================================

def test_should_place_points_correctly_in_screen_coordinates(tmp_path):
    # Arrange : p_haut a y petit → doit avoir cy petit (en haut)
    pts = [Point(200, 10), Point(200, 500), Point(50, 250), Point(350, 250)]
    svg = str(tmp_path / "t.svg")
    # Act
    export_to_svg(compute_voronoi(pts), svg, width=800, height=600)
    cy_vals = sorted(cy for _, cy in _site_circles(svg))
    cx_vals = sorted(cx for cx, _ in _site_circles(svg))
    # Assert : sans inversion Y → cy croît avec y, cx croît avec x
    assert cy_vals[-1] > cy_vals[0]
    assert cx_vals[-1] > cx_vals[0]

def test_should_spread_small_points_across_svg_and_respect_padding(small_pts_diagram, tmp_path):
    # Arrange
    svg = str(tmp_path / "t.svg")
    # Act
    export_to_svg(small_pts_diagram, svg, width=800, height=600)
    circles = _site_circles(svg)
    cx_vals = [cx for cx, _ in circles]
    # Assert : spread > 50% de la largeur
    assert max(cx_vals) - min(cx_vals) > 400
    # Assert : padding respecté (> 20px de chaque bord)
    for cx, cy in circles:
        assert 20 < cx < 780
        assert 20 < cy < 580
