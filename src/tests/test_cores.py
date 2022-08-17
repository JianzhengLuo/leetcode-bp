import pytest

from lib import cores


@pytest.mark.parametrize(
    ("name", "file", "data"),
    [("Problems", ":memory:", "./problems.json")])
def test_table_creation_from_file(name, file, data):
    with cores.Database(file) as db:
        db.create_table_from_file(name, data)
