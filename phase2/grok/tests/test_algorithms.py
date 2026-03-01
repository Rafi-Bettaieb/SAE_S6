import pytest
from geometry import Vertex
from algorithms import delaunay_triangulate, clip_line

@pytest.fixture
def clip_bounds():
    # Arrange (Fixture)
    return 0, 0, 10, 10


# --- Tests pour la triangulation ---

def test_should_return_two_triangles_given_four_points_forming_square():
    # Arrange
    points = [Vertex(0, 0), Vertex(10, 0), Vertex(0, 10), Vertex(10, 10)]

    # Act
    triangles = delaunay_triangulate(points)

    # Assert
    assert len(triangles) == 2

def test_should_raise_value_error_given_less_than_three_points():
    # Arrange
    points = [Vertex(0, 0), Vertex(10, 0)]

    # Act & Assert
    with pytest.raises(ValueError, match="Au moins 3 points sont requis"):
        delaunay_triangulate(points)


# --- Tests pour le découpage de lignes (clipping) ---

def test_should_return_original_line_given_line_completely_inside(clip_bounds):
    # Arrange
    xmin, ymin, xmax, ymax = clip_bounds
    x1, y1, x2, y2 = 2, 2, 8, 8

    # Act
    result = clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

    # Assert
    assert result == (2, 2, 8, 8)

def test_should_return_clipped_line_given_line_intersecting_bounds(clip_bounds):
    # Arrange
    xmin, ymin, xmax, ymax = clip_bounds
    x1, y1, x2, y2 = 5, 5, 15, 5

    # Act
    result = clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

    # Assert
    assert result == (5, 5, 10, 5)

def test_should_return_none_given_line_completely_outside(clip_bounds):
    # Arrange
    xmin, ymin, xmax, ymax = clip_bounds
    x1, y1, x2, y2 = 15, 15, 20, 20

    # Act
    result = clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

    # Assert
    assert result is None