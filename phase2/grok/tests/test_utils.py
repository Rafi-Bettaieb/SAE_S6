import pytest
from phase2.grok.src.geometry import Vertex
from phase2.grok.src.utils import load_points_from_file

@pytest.fixture
def mock_points_file(tmp_path):
    # Arrange (Fixture)
    test_file = tmp_path / "points_test.txt"
    content = """
    # Un commentaire
    10.5, 20.0
      30.0 ,   40.2  
    ligne invalide
    """
    test_file.write_text(content)
    return str(test_file)


# --- Tests pour le chargement des fichiers ---

def test_should_return_correct_number_of_points_given_valid_and_invalid_lines(mock_points_file):
    # Arrange
    file_path = mock_points_file

    # Act
    points = load_points_from_file(file_path)

    # Assert
    assert len(points) == 2

def test_should_parse_first_vertex_correctly_given_valid_file(mock_points_file):
    # Arrange
    file_path = mock_points_file
    expected_vertex = Vertex(10.5, 20.0)

    # Act
    points = load_points_from_file(file_path)

    # Assert
    assert points[0].equals(expected_vertex) is True

def test_should_parse_second_vertex_correctly_given_valid_file(mock_points_file):
    # Arrange
    file_path = mock_points_file
    expected_vertex = Vertex(30.0, 40.2)

    # Act
    points = load_points_from_file(file_path)

    # Assert
    assert points[1].equals(expected_vertex) is True