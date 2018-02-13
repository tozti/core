from tests.commons import db_contains_object, make_call, add_object_get_id
import json
import pytest
from uuid import UUID, uuid4


TYPE = "type/foo"


@pytest.mark.extensions("rel01")
def test_storage_rel_toone_post(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar)}}
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})
    if db.count() == 2:
        assert db_contains_object(db, bar) and db_contains_object(db, foo)
    else:
        assert False

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_owner_patch_empty(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})

    result = make_call("PATCH", "/store/resources/{}".format(uid_foo), json={"data": {"relationships": {}}})
    assert result.status_code == 500

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_owner_patch(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    bar2 = {"attributes": {"bar": "bar"}}
    uid_bar2 = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": {"data": {"id": uid_bar}}}})

    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar)}}
    assert db_contains_object(db, foo)

    result = make_call("PATCH", "/store/resources/{}".format(uid_foo), json={"data": {"relationships": {"member": {"data": {"id": uid_bar2}}}}})
    assert result.status_code == 200

    foo = {"attributes": {"foo": "foo"}, "relationships": {"member": UUID(uid_bar2)}}
    assert db_contains_object(db, foo)


@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_owner_patch(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    bar2 = {"attributes": {"bar": "bar"}}
    uid_bar2 = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}]}}})

    foo = {"attributes": {"foo": "foo"}, "relationships": {"members": [UUID(uid_bar)]}}
    assert db_contains_object(db, foo)

    result = make_call("PATCH", "/store/resources/{}".format(uid_foo), json={"data": {"relationships": {"members": {"data": [{"id": uid_bar2}]}}}})
    assert result.status_code == 200

    foo = {"attributes": {"foo": "foo"}, "relationships": {"members": [UUID(uid_bar2)]}}
    assert db_contains_object(db, foo)

@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_owner_patch_empty(tozti, db):
    bar = {"attributes": {"bar": "bar"}}
    uid_bar = add_object_get_id({"type": "rel02/bar", "attributes": {"bar": "bar"}})
    uid_foo = add_object_get_id({"type": "rel02/foo", "attributes": {"foo": "foo"}, "relationships": {"members": {"data": [{"id": uid_bar}]}}})

    foo = {"attributes": {"foo": "foo"}, "relationships": {"members": [UUID(uid_bar)]}}
    assert db_contains_object(db, foo)

    result = make_call("PATCH", "/store/resources/{}".format(uid_foo), json={"data": {"relationships": {"members": {"data": []}}}})
    assert result.status_code == 200

    foo = {"attributes": {"foo": "foo"}, "relationships": {"members": []}}
    assert db_contains_object(db, foo)
