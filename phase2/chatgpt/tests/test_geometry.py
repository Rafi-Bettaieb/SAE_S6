import pytest
from phase2.chatgpt.geometry import midpoint, perpendicular_bisector, clip_polygon


# ============================================================
# MIDPOINT TESTS
# ============================================================

def test_should_return_correct_midpoint_given_two_points():
    # Arrange
    p1 = (0, 0)
    p2 = (10, 10)

    # Act
    result = midpoint(p1, p2)

    # Assert
    assert result == (5.0, 5.0)


# ============================================================
# PERPENDICULAR BISECTOR TESTS
# ============================================================

def test_should_compute_valid_bisector_given_two_distinct_points():
    # Arrange
    p1 = (0, 0)
    p2 = (10, 0)

    # Act
    A, B, C = perpendicular_bisector(p1, p2)

    # Assert
    # Le milieu (5,0) doit appartenir à la médiatrice
    assert pytest.approx(A * 5 + B * 0 + C, abs=1e-6) == 0


def test_should_raise_exception_given_identical_points_for_bisector():
    # Arrange
    p = (2, 2)

    # Act & Assert
    with pytest.raises(Exception):
        perpendicular_bisector(p, p)


# ============================================================
# CLIP POLYGON TESTS
# ============================================================

def test_should_clip_polygon_correctly_given_vertical_half_plane():
    # Arrange
    polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
    A, B, C = 1, 0, -5   # x - 5 = 0
    keep_point = (6, 5)

    # Act
    clipped = clip_polygon(polygon, A, B, C, keep_point)

    # Assert
    assert all(p[0] >= 5 - 1e-6 for p in clipped)


def test_should_return_empty_polygon_given_full_exclusion():
    # Arrange
    polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
    A, B, C = 1, 0, -20   # x - 20 = 0
    keep_point = (30, 0)

    # Act
    clipped = clip_polygon(polygon, A, B, C, keep_point)

    # Assert
    assert clipped == []