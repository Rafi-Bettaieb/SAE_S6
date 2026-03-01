import pytest
import math
from phase2.grok.src.geometry import Vertex, Triangle

@pytest.fixture
def sample_triangle():
    # Arrange (Fixture)
    return Triangle(Vertex(0, 0), Vertex(0, 4), Vertex(3, 0))


# --- Tests pour Vertex.equals ---

def test_should_return_true_given_identical_vertices():
    # Arrange
    v1 = Vertex(1.0, 2.0)
    v2 = Vertex(1.0, 2.0)

    # Act
    is_equal = v1.equals(v2)

    # Assert
    assert is_equal is True

def test_should_return_true_given_vertices_within_tolerance():
    # Arrange
    v1 = Vertex(1.0, 2.0)
    v2 = Vertex(1.0000000001, 2.0)

    # Act
    is_equal = v1.equals(v2)

    # Assert
    assert is_equal is True

def test_should_return_false_given_different_vertices():
    # Arrange
    v1 = Vertex(1.0, 2.0)
    v2 = Vertex(1.5, 2.0)

    # Act
    is_equal = v1.equals(v2)

    # Assert
    assert is_equal is False


# --- Tests pour le calcul du cercle circonscrit ---

def test_should_calculate_correct_center_x_given_valid_triangle(sample_triangle):
    # Arrange
    triangle = sample_triangle

    # Act
    center_x = triangle.circumcircle['c'].x

    # Assert
    assert math.isclose(center_x, 1.5, abs_tol=1e-9)

def test_should_calculate_correct_center_y_given_valid_triangle(sample_triangle):
    # Arrange
    triangle = sample_triangle

    # Act
    center_y = triangle.circumcircle['c'].y

    # Assert
    assert math.isclose(center_y, 2.0, abs_tol=1e-9)

def test_should_calculate_correct_radius_given_valid_triangle(sample_triangle):
    # Arrange
    triangle = sample_triangle

    # Act
    radius = triangle.circumcircle['r']

    # Assert
    assert math.isclose(radius, 2.5, abs_tol=1e-9)

def test_should_raise_value_error_given_collinear_points():
    # Arrange
    v0 = Vertex(0, 0)
    v1 = Vertex(1, 1)
    v2 = Vertex(2, 2)

    # Act & Assert
    with pytest.raises(ValueError, match="Points colinéaires"):
        Triangle(v0, v1, v2)


# --- Tests pour in_circumcircle ---

def test_should_return_true_given_point_at_center(sample_triangle):
    # Arrange
    triangle = sample_triangle
    point = Vertex(1.5, 2.0)

    # Act
    is_inside = triangle.in_circumcircle(point)

    # Assert
    assert is_inside is True

def test_should_return_true_given_point_on_border(sample_triangle):
    # Arrange
    triangle = sample_triangle
    point = Vertex(3, 4)

    # Act
    is_inside = triangle.in_circumcircle(point)

    # Assert
    assert is_inside is True

def test_should_return_false_given_point_outside(sample_triangle):
    # Arrange
    triangle = sample_triangle
    point = Vertex(5, 5)

    # Act
    is_inside = triangle.in_circumcircle(point)

    # Assert
    assert is_inside is False