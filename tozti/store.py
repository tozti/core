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
from collections import namedtuple
from datetime import datetime, timezone
from uuid import uuid4

import aiohttp
from aiohttp.web import json_response
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from motor.motor_asyncio import AsyncIOMotorClient

from tozti import logger
from tozti.utils import RouterDef, register_error, api_error


register_error('RESOURCE_NOT_FOUND', 'resource {id} not found', 404)
register_error('NOT_JSON', 'expected json data', 406)
register_error('BAD_JSON', 'malformated json data', 400)
register_error('INVALID_DATA', 'invalid submission: {err}', 400)


########
# Routes

router = RouterDef()

uuid_re = '-'.join('[0-9a-fA-F]{%d}' % i for i in (8, 4, 4, 4, 12))
relationship_re = r'[\da-z]+'
resources = router.add_resource('/resources')
resources_single = router.add_resource('/resources/{id:%s}' % uuid_re)
relationship = router.add_resource('/resources/{id:%s}/{rel:%s}' % uuid_re, relationship_re)


@resources.post
async def resources_post(req):
    """POST /api/store/resources
    """
    if req.content_type != 'application/json':
        return api_error('NOT_JSON')
    try:
        data = await req.json()
    except JSONDecodeError:
        return api_error('BAD_JSON')
    try:
        id = await req.app['tozti-store'].create(data)
    except ValueError as err:
        return api_error('INVALID_DATA', err=err)
    return json_response(await req.app['tozti-store'].get(id))


@resources_single.get
async def resources_get(req):
    """GET /api/store/resources
    """
    id = req.match_info['id']
    try:
        return json_response(await req.app['tozti-store'].get(id))
    except KeyError:
        return api_error('RESOURCE_NOT_FOUND', id=id)

@resources_single.patch
async def resources_patch(req):
    pass

@resources_single.delete
async def resources_delete(req):
    id = req.match_info['id']
    try:
        req.app['tozti-store'].remove(id)
    except KeyError:
        return api_error('RESOURCE_NOT_FOUND', id=id)


@relationship.get
async def relationship_get(req):
    id = req.match_info['id']
    rel = req.match_info['rel']
    try:
        resp = await req.app['tozti-store'].get(id)
        return json_response(resp[rel])
    except KeyError:
        return api_error('RESOURCE_NOT_FOUND', id=id)

@relationship.put
async def relationship_put(req):
    pass

@relationship.post
async def relationship_post(req):
    pass


#########
# Backend

async def open_db(app):
    """Initialize storage backend at app startup."""
    app['tozti-store'] = Store(**app['tozti-config']['mongodb'])


async def close_db(app):
    """Close storage backend at app cleanup."""
    await app['tozti-store'].close()


Schema = namedtuple('Schema', ('attributes', 'relationships'))


class TypeCache:
    def __init__(self):
        self._cache = {}

    async def __getitem__(self, type_url):
        if type_url in self._cache:
            return self._cache[type_url]

        async with aiohttp.ClientSession() as session:
            async with session.get(type_url) as resp:
                assert resp.status == 200
                raw_schema = await resp.json()

        schema = Schema(**raw_schema)
        self._cache[type_url] = schema

        return schema

    def validate_relationships(self, relationships):
        forbidden_keys = {'creator', 'self'}
        if not (forbidden_keys & relationships.keys()).empty():
            raise ValueError("forbidden key used in relationships")

    async def validate(self, data):
        schema = await self[data['type']]
        try:
            validate(data['attributes'], schema.attributes)
        except ValidationError as err:
            raise ValueError(err.message)
        validate_relationships(data['relationships'])


#FIXME: how do we get the hostname? config file?
BASE_URL = 'http://localhost'

class Store:
    def __init__(self, **kwargs):
        self._client = AsyncIOMotorClient(**kwargs)
        self._resources = self._client.tozti.resources
        self._typecache = TypeCache()

    async def _render(self, rep):
        """Take internal representation and return it in an HTTP-API format."""

        res_url = lambda id: '%s/resources/%s' % (BASE_URL, id)
        rel_url = lambda id, rel: '%s/resources/%s/%s' % (BASE_URL, id, rel)

        id = rep['_id']

        out = {
            'type': rep['type'],
            'id': id,
            'attributes': rep['attributes'],
            'meta': {
                'created': rep['created'],
                'last-modified': rep['last-modified'],
            },
            'relationships': {
                'self': {'data': res_url(id)},
            },
        }

        schema = await self._typecache[rep['type']]
        for (rel, val) in schema.relationships:
            if 'reverse-of' in val:
                data = await self._resources.find({'relationships': {rel: id}})
            elif val.get('arity', 'one') == 'one':
                data = res_url(rep['relationships'][rel])
            else:
                data = [res_url(i) for i in rep['relationships'][rel]]

            out['relationships'][rel] = {
                'self': rel_url(id, rel),
                'data': data,
            }

        return out

    async def create(self, data):
        """Take python dict from http request and add it to the db."""
        logger.debug('incoming data: {}'.format(data))
        if 'type' not in data:
            raise ValueError('missing type property')

        # sanitization, keep just the allowed non-autogenerated properties
        attributes = data.get('attributes', {})
        relationships = data.get('relationships', {})
        meta = data.get('meta', {})
        resource_type = data['type']
        data = {'attributes': attributes, 'relationships': relationships,
                'meta': meta, 'type': resource_type}

        await self._typecache.validate(data)
        await self._resources.insert_one(data)

    async def get(self, id):
        logger.debug('querying DB for resource {}'.format(id))
        resp = await self._resources.find_one({'_id': id})
        if resp is None:
            raise KeyError
        return await self._render(resp)

    async def update(self, id, data):
        pass

    async def remove(self, id):
        logger.debug('deleting resource {} from the DB'.format(id))
        result = await self._resources.delete_one({'_id': id})
        if result.deleted_count == 0:
            raise KeyError

    async def rel_get(self, id, rel):
        pass

    async def rel_update(self, id, rel, data):
        pass

    async def rel_append(self, id, rel, data):
        pass

    async def close(self):
        pass
