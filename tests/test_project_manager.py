from app import ProjectManager


def test_validate_structure_minimal():
    pm = ProjectManager()
    good = {
        "title": "T",
        "cover_page": {"id": "cover", "title": "封面"},
        "pages": [],
        "config": {}
    }
    assert pm.validate_structure(good) is True

    bad = {"title": "T", "pages": []}
    assert pm.validate_structure(bad) is False
