# -*- coding:utf-8 -*-

# This file is part of Tozti.

# Tozti is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Tozti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Tozti.  If not, see <http://www.gnu.org/licenses/>.


from json import JSONDecodeError
from uuid import UUID

import tozti
from tozti.utils import RouterDef, NotJsonError, BadJsonError, json_response
from tozti.store import logger


# Regex of an UUID as hexdigit string
UUID_RE = '-'.join('[0-9a-fA-F]{%d}' % i for i in (8, 4, 4, 4, 12))
# Regex for validating whether a string is a valid type name.
# Here, valid type names are arbitrary alphanumeric strings
# with '-', '_' and at most one '/'
TYPE_RE = '([\w-]+/)?[\w-]+'


router = RouterDef()
resources = router.add_route('/resources')
resources_single = router.add_route('/resources/{id:%s}' % UUID_RE)
relationship = router.add_route('/resources/{id:%s}/{rel}' % UUID_RE)
types = router.add_route('/by-type/{type:%s}' % TYPE_RE)
by_handle = router.add_route('/by-handle/{handle}')


async def get_json_from_request(req):
    if req.content_type != 'application/vnd.api+json':
        raise NotJsonError()
    try:
        data = await req.json()
    except JSONDecodeError:
        raise BadJsonError()
    return data


@resources.post
async def resources_post(req):
    """Request handler for ``POST /api/store/resources``."""

    data = await get_json_from_request(req)
    resource = await req.app['tozti-store'].create(data, req['user'])
    return json_response({'data': resource})


@resources_single.get
async def resources_get(req):
    """Request handler for ``GET /api/store/resources/{id}``."""

    id = UUID(req.match_info['id'])
    return json_response({'data': await req.app['tozti-store'].read(id)})


@resources_single.patch
async def resources_patch(req):
    """Request handler for ``PATCH /api/store/resources/{id}``."""

    data = await get_json_from_request(req)
    id = UUID(req.match_info['id'])
    await req.app['tozti-store'].update(id, data)
    return json_response({'data': await req.app['tozti-store'].read(id)})


@resources_single.delete
async def resources_delete(req):
    """Request handler for ``DELETE /api/store/resources/{id}``."""

    id = UUID(req.match_info['id'])
    await req.app['tozti-store'].delete(id)
    return json_response({})


@relationship.get
async def relationship_get(req):
    """Request handler for ``GET /api/store/resources/{id}/{rel}``."""

    id = UUID(req.match_info['id'])
    rel = req.match_info['rel']
    return json_response({'data': await req.app['tozti-store'].item_read(id, rel)})


@relationship.put
async def relationship_put(req):
    """Request handler for ``PUT /api/store/resources/{id}/{rel}``."""

    id = UUID(req.match_info['id'])
    rel = req.match_info['rel']

    store = req.app['tozti-store']

    type_name = await store.type_by_id(id)
    schema = store._types[type_name]

    if rel in schema and schema[rel].is_upload:
        await store.item_upload(id, rel, req.content_type, req.content)

    else:
        data = await get_json_from_request(req)
        await store.item_update(id, rel, data)
    return json_response({'data': await req.app['tozti-store'].item_read(id, rel)})


@relationship.post
async def relationship_post(req):
    """Request handler for ``POST /api/store/resources/{id}/{rel}``."""

    data = await get_json_from_request(req)
    id = UUID(req.match_info['id'])
    rel = req.match_info['rel']

    await req.app['tozti-store'].item_append(id, rel, data)
    return json_response({'data': await req.app['tozti-store'].item_read(id, rel)})


@relationship.delete
async def relationship_delete(req):
    """Request handler for ``DELETE /api/store/resources/{id}/{rel}``"""

    data = await get_json_from_request(req)
    id = UUID(req.match_info['id'])
    rel = req.match_info['rel']

    await req.app['tozti-store'].item_remove(id, rel, data)
    return json_response({'data': await req.app['tozti-store'].item_read(id, rel)})


@types.get
async def types_get(req):
    """Request handler for ``GET /api/store/by-type/{type}``."""

    type = req.match_info['type']
    return json_response({'data': await req.app['tozti-store'].resources_by_type(type)})


@by_handle.get
async def by_handle_get(req):
    """Request handler for ``GET /by-handle/{handle}``."""

    handle = req.match_info['handle']
    store = req.app['tozti-store']
    return json_response({'data': await store.by_handle(handle)})


@by_handle.post
async def by_handle_post(req):
    """Request handler for ``POST /by-handle/{handle}``."""

    handle = req.match_info['handle']
    store = req.app['tozti-store']
    data = await get_json_from_request(req)

    await store.handle_set(handle, data, allow_overwrite=False)
    return json_response({'data': await store.by_handle(handle)})


@by_handle.put
async def by_handle_put(req):
    """Request handler for ``PUT /by-handle/{handle}``."""

    handle = req.match_info['handle']
    store = req.app['tozti-store']
    data = await get_json_from_request(req)

    await store.handle_set(handle, data, allow_overwrite=True)
    return json_response({'data': await store.by_handle(handle)})


@by_handle.delete
async def by_handle_delete(req):
    """Request handler for ``PUT /by-handle/{handle}``."""

    handle = req.match_info['handle']
    store = req.app['tozti-store']
    await store.handle_delete(handle)

    return json_response({})


async def open_db(app, types):
    """Initialize storage backend at app startup."""

    from tozti.store.engine import Store

    app['tozti-store'] = Store(types, **tozti.CONFIG['mongodb'])


async def close_db(app):
    """Close storage backend at app cleanup."""

    await app['tozti-store'].close()
