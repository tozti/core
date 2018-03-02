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


import os.path
from datetime import datetime, timezone
from uuid import uuid4, UUID
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from tozti.store import logger, NoResourceError, NoTypeError, BadItemError, NoItemError, NoHandleError, HandleExistsError
from tozti.store.schema import Schema, fmt_resource_url
from tozti.utils import BadDataError, ValidationError, validate, NotAcceptableError, current_time

from tozti.auth.utils import LoginUnknown as LoginUnknown


def fmt_upload_url(id):
    return 'http://{hostname}/uploads/{id}'.format(
        id=id, hostname=tozti.CONFIG['http']['hostname'])


class Store:
    def __init__(self, types, **kwargs):
        self._client = AsyncIOMotorClient(**kwargs)
        self._db = self._client.tozti
        self._types = {k: Schema(k, v, db=self) for (k, v) in types.items()}

    async def resource_by_id(self, id, projection=None):
        """Returns the raw resource with given id.

        `id` must be an instance of `uuid.UUID`. Raises `NoResourceError` if
        the resource is not found.
        """

        logger.debug('querying DB for resource {}'.format(id))
        res = await self._db.resources.find_one({'_id': id}, projection=projection)
        if res is None:
            raise NoResourceError(id=id)

        handle = await self._db.handles.find_one({'target': id})
        if handle is not None:
            res['handle'] = handle['_id']

        return res

    async def type_by_id(self, id):
        """Return the type URL of a given resource.

        `id` must be an instance of `uuid.UUID`. Raises `NoResourceError` if
        the resource is not found.
        """

        logger.debug('querying DB for type of resource {}'.format(id))
        res = await self.resource_by_id(id, {'type': 1})
        return res['type']

    async def create(self, raw, user=None):
        """Create a new resource and return it's rendered form.

        The passed data must be the content of the request as specified by
        JSON API. See https://jsonapi.org/format/#crud-creating.
        """

        try:
            tp = raw['data']['type']
        except (TypeError, KeyError):
            raise BadDataError('invalid data: type must be specified')

        if tp not in self._types:
            raise NoTypeError(type=tp)
        schema = self._types[tp]

        data = await schema.sanitize(raw)
        data['_id'] = uuid4()

        time = current_time()
        data['meta'] = {
            'created': time,
            'last-modified': time
        }
        if user is not None:
            data['meta']['author'] = user

        await self._db.resources.insert_one(data)

        return await schema.render(data)

    async def read(self, id):
        """Query the DB for a resource.

        `id` must be an instance of `uuid.UUID`. Raises `NoResourceError` if
        the resource is not found. The answer is a JSON API _resource object_.
        See https://jsonapi.org/format/#document-resource-objects.
        """

        res = await self.resource_by_id(id)
        schema = self._types[res['type']]
        return await schema.render(res)

    async def update(self, id, raw):
        """Update a resource in the DB.

        `id` must be an instance of `uuid.UUID`. Raises `NoResourceError` if
        the resource is not found. `raw` must be the content of the request as
        specified by JSON API. See https://jsonapi.org/format/#crud-updating.
        """

        schema = self._types[await self.type_by_id(id)]
        data = await schema.sanitize(raw, is_create=False)
        if len(data) > 0:
            data['meta.last-modified'] = current_time()
            await self._db.resources.update_one({'_id': id}, {'$set': data})

    async def delete(self, id):
        """Remove a resource from the DB.

        `id` must be an instance of `uuid.UUID`. Raises KeyError if the
        resource is not found.
        """

        logger.debug('Deleting resource {} from the DB'.format(id))
        result = await self._db.resources.delete_one({'_id': id})
        if result.deleted_count == 0:
            raise NoResourceError(id=id)

    async def item_read(self, id, key):
        schema = self._types[await self.type_by_id(id)]
        if key not in schema:
            raise NoItemError(key=key, status=404)

        data = await self.resource_by_id(id, {'body.%s' % key: 1})
        return await schema[key].render(id, data['body'].get(key))

    async def item_update(self, id, key, raw):
        schema = self._types[await self.type_by_id(id)]

        try:
            data = await schema[key].sanitize(raw)
        except NoItemError as err:
            err.status = 404
            raise err

        await self._db.resources.update_one(
            {'_id': id},
            {'$set': {'body.%s' % key: data}})

    async def item_upload(self, id, rel, content_type, content):
        schema = self._types[await self.type_by_id(id)]

        if content_type not in schema[rel].acceptable:
            raise NotAcceptableError()
        blob_id = uuid4()
        path = os.path.join(tozti.CONFIG['http']['upload_dir'], str(blob_id))
        with open(path, 'wb') as stream:
            async for chunk, _ in content.iter_chunks():
                stream.write(chunk)

        await self._db.resources.update_one(
            {'_id': id},
            {'$set': {'body.%s' % rel: fmt_upload_url(blob_id),
                      'meta.last-modified': current_time()}})

    async def item_append(self, id, key, raw):
        schema = self._types[await self.type_by_id(id)]

        if key not in schema:
            raise NoItemError(key=key, status=404)

        if schema[key].is_array:
            data = await schema[key].sanitize(raw)

            await self._db.resources.update_one(
                {'_id': id},
                {'$addToSet': {'body.%s' % key: {'$each': data}},
                 '$set': {'meta.last-modified': current_time()}})

        elif schema[key].is_dict:
            data = await schema[key].sanitize(raw)

            await self._db.resources.update_one(
                {'_id': id},
                {'$set': {**{'body.%s.%s' % (key, k): v for (k, v) in data.items()},
                          'meta.last-modified': current_time()}})

        else:
            raise BadItemError('body item {key} is not an array', key=key)

    async def item_remove(self, id, key, raw):
        schema = self._types[await self.type_by_id(id)]

        if key not in schema:
            raise NoItemError(key=key, status=404)

        if schema[key].is_array:
            data = await schema[key].sanitize(raw, check_consistency=False)

            await self._db.resources.update_one(
                {'_id': id},
                {'$pull': {'body.%s' % key: {'id': {'$in': [UUID(x['id']) for x in data]}}},
                 '$set': {'meta.last-modified': current_time()}})

        elif schema[key].is_dict:
            data = await schema[key].sanitize(raw, check_consistency=False)

            await self._db.resources.update_one(
                {'_id': id},
                {'$unset': {'body.%s.%s' % (key, k): '' for k in data},
                 '$set': {'meta.last-modified': current_time()}})

        else:
            raise BadItemError('body item {key} is not an array', key=key)

    async def resources_by_type(self, type):
        logger.debug('Querying type %s' % type)
        if type not in self._types:
            raise NoTypeError(type=type, status=404)

        cursor = self._db.resources.find({'type': type}, ['_id'])
        links = []
        async for hit in cursor:
            links.append({'id': hit['_id'],
                          'type': type,
                          'href': fmt_resource_url(hit['_id'])})
        return links

    async def by_handle(self, handle):
        doc = await self._db.handles.find_one({'_id': handle})
        if doc is None:
            raise NoHandleError(handle=handle)
        return {'id': doc['target'],
                'type': doc['type'],
                'href': fmt_resource_url(doc['target'])}

    async def handle_set(self, handle, raw, allow_overwrite):
        try:
            assert len(raw) == 1
            assert len(raw['data']) == 1
            id = UUID(raw['data']['id'])
        except:
            raise BadDataError()

        if not allow_overwrite and (await self._db.handles.find({'_id': handle}).count()) > 0:
            raise HandleExistsError(handle)
        await self.handle_set_id(handle, id)

    async def handle_set_id(self, handle, id):
        type = await self.type_by_id(id)
        await self._db.handles.update_one(
            {'_id': handle},
            {'$set': {'target': id, 'type': type}},
            upsert=True)

    async def handle_delete(self, handle):
        res = await self._db.handles.delete_one({'_id': handle})
        if res.deleted_count == 0:
            raise NoHandleError(handle=handle)

    async def close(self):
        """Close the connection to the MongoDB server."""

        self._client.close()
