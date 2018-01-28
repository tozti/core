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



"""
Now, tests for ressources \o/
"""
@pytest.mark.extensions("rel01")
def test_storage_rel_toone_notspecified(tozti, db):
    assert make_call("POST", "/store/resources", json = {"data": {"type": "rel01/foo", "attributes": {"foo": "foo"}}}).status_code == 400


@pytest.mark.extensions("rel02")
def test_storage_rel_tomany_notspecified(tozti, db):
    assert make_call("POST", "/store/resources", json = {"data": {"type": "rel02/foo", "attributes": {"foo": "foo"}}}).status_code == 200

@pytest.mark.extensions("rel01")
def test_storage_rel_toone_badrelerror(tozti, db):
    """ Test coming from a bug in tozti: at first, their was a typo in _santize_to_one
    with the presence of `BadRelData` instead of `BadRelError`.
    The test in itself doesn't mean anything, it is just here for this precise error
    """
    uid_bar = add_object_get_id({"type": "rel01/bar", "attributes": {"bar": "bar"}})
    assert make_call("POST", 
                    "/store/resources",
                    {"type": "rel01/foo", "attributes": {"foo": "foo"}, "relationships": {"member": uid_bar}}
                    ).status_code == 400

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