from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("type")
@pytest.mark.parametrize("json", [
    {"type": TYPE,
         "attributes": {"name": "f", "email": "a@a.com"}},
    ])
def test_storage_delete_object(tozti, db, json):
    try:
        uid = add_object_get_id(json)
        c = db.count()
        make_call("DELETE", "/store/resources/{}".format(uid))
        assert c > db.count()
    except:
        assert False


def test_storage_delete_object_fail_not_uuid(tozti, db):
    assert make_call("DELETE", "/store/resources/foo").status_code == 404


def test_storage_delete_object_fail_uuid(tozti, db):
    assert make_call("DELETE", "/store/resources/00000000-0000-0000-0000-000000000000").status_code == 404


