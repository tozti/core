from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("type")
@pytest.mark.parametrize("json, expected", [
    ({"type": TYPE, "attributes": {"name": "f", "email": "a@a.com"}},   True),
    ({"type": TYPE, "THISISNOTATYPO": {"name": "f", "email": "a@a.com"}},  False),
    ({"type": TYPE, "attributes": {"name": "f", "email": "a"}},         False),
    ({"type": TYPE, "attributes": {"name": "f"}},                       False),
    ({"type": TYPE, "attributes": {"name": "f", "foo": "b"}},           False)
    ])
def test_storage_post_request(tozti, db, json, expected):
    ret_val = make_call("POST", '/store/resources', json={"data": json})
    if ret_val.status_code == 200:
        if db.count() == 1:
            assert db_contains_object(db, json) == expected
        else:
            assert not expected
    else:
        assert not expected

def test_storage_post_no_content(tozti, db):
    assert make_call("POST", '/store/resources').status_code == 400

