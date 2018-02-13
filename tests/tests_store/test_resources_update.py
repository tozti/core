from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"

@pytest.mark.extensions("type")
@pytest.mark.parametrize("json, diff, expected", [
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}, {"name": "g"},        True),
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}, {},                   False),
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}, {"email": "b@b.com"}, True),
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}, {"email": "a"},       False),
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}, {"bar": "a"},         False),
    ])
def test_storage_update(tozti, db, json, diff, expected):
    try:
        uid = add_object_get_id(json)
        result = make_call("PATCH", "/store/resources/{}".format(uid), json={"data": {"attributes": diff}})
        # test if the request succeeded
        if result.status_code == 200:
            theory = json
            for (k, v) in diff.items():
                if k in theory["attributes"]:
                    theory["attributes"][k] = v
            if db.count() == 1:
                assert db_contains_object(db, theory) == expected
            else:
                assert not expected
        else:
            assert not expected
    except:
        assert False

@pytest.mark.extensions("type")
def test_storage_update_no_content(tozti, db):
    json = {"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}}
    uid = add_object_get_id(json)
    assert make_call("PATCH", "/store/resources/{}".format(uid)).status_code == 400

def test_storage_update_object_fail_not_uuid(tozti, db):
    assert make_call("PATCH", "/store/resources/foo").status_code == 404

def test_storage_update_object_fail_uuid(tozti, db):
    assert make_call("PATCH", "/store/resources/00000000-0000-0000-0000-000000000000").status_code == 400

