from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("rel02")
def test_storage_type_get(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    resp = make_call("GET", "/store/by-type/rel02/bar")
    data = resp.json()['data']
    ids = {d['id'] for d in data}

    assert ids == {uid_bar, uid_bar2}

@pytest.mark.extensions("rel02")
def test_storage_type_get_empty(tozti, db):
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": []}}})

    resp = make_call("GET", "/store/by-type/rel02/bar")
    data = resp.json()['data']

    assert len(data) == 0

@pytest.mark.extensions("rel02")
def test_storage_type_get_nonexistent(tozti, db):
    resp = make_call("GET", "/store/by-type/")
    assert resp.status_code == 404

    resp = make_call("GET", "/store/by-type/nonexistent")
    assert resp.status_code == 404

    resp = make_call("GET", "/store/by-type/a/bit/long")
    assert resp.status_code == 404
