from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("rel01")
def test_storage_rel_toone_delete(tozti, db):
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})

    assert make_call("DELETE", "/store/resources/{}/member".format(uid_foo), json={'data':[{'id': uid_bar}]}).status_code == 403

@pytest.mark.extensions("rel02")
def test_storage_rel_delete_single_existing(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    resp = make_call("DELETE", "/store/resources/{}/members".format(uid_foo), json={'data':[{'id': uid_bar}]})
    resp_ids = {l['id'] for l in resp.json()['data']['data']}

    assert uid_bar not in resp_ids
    assert uid_bar2 in resp_ids

@pytest.mark.extensions("rel02")
def test_storage_rel_delete_multiple_existing(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    resp = make_call("DELETE", "/store/resources/{}/members".format(uid_foo), {'data':[{'id': uid_bar}, {'id': uid_bar2}]})
    resp_ids = {l['id'] for l in resp.json()['data']['data']}

    assert len(resp_ids) == 0

@pytest.mark.extensions("rel02")
def test_storage_rel_delete_single_missing(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    make_call("DELETE", "/store/resources/{}".format(uid_bar))

    resp = make_call("DELETE", "/store/resources/{}/members".format(uid_foo), {'data':[{'id': uid_bar}]})
    resp_ids = {l['id'] for l in resp.json()['data']['data']}

    assert {uid_bar2} == resp_ids

@pytest.mark.extensions("rel02")
def test_storage_rel_delete_from_missing(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    resp = make_call("DELETE", "/store/resources/{}/does_not_exist".format(uid_foo), {'data':[{'id': uid_bar}]})
    assert resp.status_code == 404

@pytest.mark.extensions("rel02")
def test_storage_rel_delete_from_nonexisting_resource(tozti, db):
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}, {"id": uid_bar2}]}}})

    resp = make_call("DELETE", "/store/resources/{}/does_not_exist".format(uid_foo), {'data':[{'id': uid_bar}]})
    random_uid = uuid4().hex
    resp = make_call("DELETE", "/store/resources/{}/members".format(random_uid), {'data':[{'id': uid_bar}]})
    assert resp.status_code == 404

