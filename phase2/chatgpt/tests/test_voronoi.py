import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from voronoi import VoronoiDiagram
# ============================================================
# BASIC CONFIGURATIONS
# ============================================================

def test_should_generate_two_cells_given_two_points():
    # Arrange
    points = [(0, 0), (10, 0)]
    bbox = [(-10, -10), (20, -10), (20, 10), (-10, 10)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == 2
    assert all(len(cell) > 0 for cell in cells)


def test_should_generate_three_cells_given_triangle_configuration():
    # Arrange
    points = [(0, 0), (10, 0), (5, 8)]
    bbox = [(-20, -20), (30, -20), (30, 30), (-20, 30)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == 3
    assert all(len(cell) >= 3 for cell in cells)


def test_should_generate_four_cells_given_square_configuration():
    # Arrange
    points = [(0, 0), (10, 0), (10, 10), (0, 10)]
    bbox = [(-20, -20), (30, -20), (30, 30), (-20, 30)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == 4


# ============================================================
# DEGENERATE CASES
# ============================================================

def test_should_handle_colinear_points_given_horizontal_alignment():
    # Arrange
    points = [(0, 0), (5, 0), (10, 0)]
    bbox = [(-20, -20), (30, -20), (30, 20), (-20, 20)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == 3
    assert all(len(cell) > 0 for cell in cells)


def test_should_handle_large_coordinates_without_error():
    # Arrange
    points = [(10000, 10000), (20000, 10000), (15000, 20000)]
    bbox = [(0, 0), (30000, 0), (30000, 30000), (0, 30000)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == 3


# ============================================================
# ROBUSTNESS
# ============================================================

def test_should_not_crash_given_random_configuration():
    # Arrange
    points = [(2, 2), (4, 3), (6, 2), (4, 1), (5, 5), (1, 4)]
    bbox = [(-10, -10), (20, -10), (20, 20), (-10, 20)]
    diagram = VoronoiDiagram(points, bbox)

    # Act
    cells = diagram.compute()

    # Assert
    assert len(cells) == len(points)