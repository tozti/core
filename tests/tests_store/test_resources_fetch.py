from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"

@pytest.mark.extensions("type")
@pytest.mark.parametrize("json", [
    {"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}},
    ])
def test_storage_get_object(tozti, db, json):
    try:
        uid = add_object_get_id(json)
        result = make_call("GET", "/store/resources/{}".format(uid)).json()["data"]
        expected = json
        expected["id"] = uid
        assert uid == result["id"] and json["attributes"] == result["attributes"]
    except:
        assert False


def test_storage_get_object_fail_not_uuid(tozti, db):
    assert make_call("GET", "/store/resources/foo").status_code == 404


def test_storage_get_object_fail_uuid(tozti, db):
    assert make_call("GET", "/store/resources/00000000-0000-0000-0000-000000000000").status_code == 404

