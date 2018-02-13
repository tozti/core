from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("rel01")
def test_storage_rel_toone_get(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar)}}
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})

    result = make_call("GET", "/store/resources/{}/member".format(uid_foo))
    assert result.json()["data"]["data"]["id"] == uid_bar

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_get_from_nonexisting_ressource(tozti, db):
    assert make_call("GET", "/store/resources/zetert/member").status_code == 404

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_get_deleted(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar)}}
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})

    make_call("DELETE", "/store/resources/{}".format(uid_bar))

    assert make_call("GET", "/store/resources/{}/member".format(uid_foo)).status_code == 404

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_get_badname(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar)}}
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})
    assert make_call("GET", "/store/resources/{}/member2".format(uid_foo)).status_code == 404

@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_get(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    result = make_call("GET", "/store/resources/{}/members".format(uid_foo))
    assert set(x["id"] for x in result.json()["data"]["data"]) == set([uid_bar, uid_bar2])

@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_get_deleted(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    make_call("DELETE", "/store/resources/{}".format(uid_bar))

    assert make_call("GET", "/store/resources/{}/member".format(uid_foo)).status_code == 404

@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_get_empty(tozti, db):
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": []}}})
    result = make_call("GET", "/store/resources/{}/members".format(uid_foo))
    assert len(result.json()["data"]["data"]) == 0

