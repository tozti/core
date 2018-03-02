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


from uuid import UUID

import jsonschema
from jsonschema import validate, ValidationError

import tozti
from tozti.store import BadAttrError, BadItemError, BadRelError, NoItemError, NoResourceError
from tozti.store.routes import UUID_RE
from tozti.utils import validate, ValidationError, BadDataError


def fmt_resource_url(id):
    return 'http://%s/api/store/resources/%s' % (
        tozti.CONFIG['http']['hostname'], id)


def fmt_relationship_url(id, rel):
    return 'http://%s/api/store/resources/%s/%s' % (
        tozti.CONFIG['http']['hostname'], id, rel)


class Schema:
    META_SCHEMA = {
        'type': 'object',
        'properties': {
            'body': {
                'type': 'object',
                'patternProperties': {'.*': {'type': 'object'}}
            },
            'optional': {
                'type': 'array',
                'items': {'type': 'string'},
            },
        },
        'additionalProperties': False,
        'required': ['body'],
    }

    SCHEMA = {
        'type': 'object',
        'properties': {
            'data': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string'},
                    'body': {'type': 'object'},
                },
                'required': ['body'],
                'additionalProperties': True,  # possible security problem
            },
        },
        'additionalProperties': False,
        'required': ['data'],
    }

    def __init__(self, name, raw, *, db):
        try:
            validate(raw, Schema.META_SCHEMA)
        except ValidationError as err:
            raise ValueError('invalid schema: %s' % err.message)

        self._defs = {}
        for (key, val_def) in raw['body'].items():
            if 'type' in val_def and val_def['type'] == 'relationship':
                self._defs[key] = RelationshipModel(key, val_def, db=db)
            elif 'type' in val_def and val_def['type'] == 'upload':
                self._defs[key] = UploadModel(
                    key, val_def['acceptable'], db=db)
            else:
                self._defs[key] = AttributeModel(key, val_def, db=db)

        self._optional = raw.get('optional', [])

        self.name = name
        self.db = db

    async def sanitize(self, raw, *, is_create=True):
        """Verify the body posted for entity creation or update.

        Returns a partial internal representation, that is a dictionary with
        `type` and `body` validated.
        """

        try:
            validate(raw, Schema.SCHEMA)
        except ValidationError as err:
            raise BadDataError(err.message)

        data = raw['data']
        if not is_create and 'type' in data:
            raise BadDataError('cannot specify type on resource update')

        # check that all and only these attributes are present
        sub1 = data['body'].keys() - self._defs.keys()
        sub2 = {k for (k, v) in self._defs.items(
        ) if v.writeable and k not in self._optional} - data['body'].keys()
        if len(sub1) > 0:
            raise NoItemError(key=sub1.pop())
        if is_create and len(sub2) > 0:
            raise BadItemError(key=sub2.pop(), msg='missing from body')

        body = {}
        for (key, value) in data['body'].items():
            body[key] = await self[key].sanitize(value)

        if is_create:
            return {'type': data['type'], 'body': body}
        else:
            return {'body.%s' % k: v for (k, v) in body.items()}

    async def render(self, rep):
        """Render a resource object given it's internal representation.

        See https://jsonapi.org/format/#document-resource-objects.
        """

        id = rep['_id']

        body = {}
        for (key, schema) in self._defs.items():
            body[key] = await schema.render(id, rep['body'].get(key))

        meta = {'created': rep['meta']['created'].isoformat() + 'Z',
                'last-modified': rep['meta']['last-modified'].isoformat() + 'Z'}
        if 'handle' in rep:
            meta['handle'] = rep['handle']
        if 'author' in rep['meta']:
            meta['author-id'] = rep['meta']['author']

        return {'id': id,
                'href': fmt_resource_url(id),
                'type': rep['type'],
                'body': body,
                'meta': meta
                }

    def __getitem__(self, key):
        if key not in self._defs:
            raise NoItemError(key=key)
        return self._defs[key]

    def __contains__(self, key):
        return key in self._defs


class LinkageModel:
    def __init__(self, targets, *, db):
        self.db = db
        if isinstance(targets, str):
            self.targets = [targets]
        else:
            self.targets = targets

    async def sanitize(self, linkage):
        """Verify that a given linkage is valid.

        Checks if the target exists and if the given type (if any) is valid.
        Returns the UUID of the target.
        """

        target = UUID(linkage['id'])
        try:
            type_url = await self.db.type_by_id(target)
        except NoResourceError:
            raise BadRelError('linked resource %s does not exist' % target)
        # FIXME: this error leaks type information, check if user can read
        # linked resource first
        if 'type' in linkage and linkage['type'] != type_url:
            raise BadRelError('mismatched type for linked resource {target}: '
                              'given: {given}, real: {real}', target=target,
                              given=linkage['type'], real=type_url)
        if self.targets is not None and type_url not in self.targets:
            raise BadRelError('unallowed type {given} for linked resource {target}',
                              given=type_url, target=target)
        return {'id': target, 'type': type_url}

    def render(self, target):
        """Render a resource object linkage.

        Does not catch KeyError in case the target is not found. The divergence
        from the spec is that we include an `href` property which is an URI
        resolving to the given target resource.

        See https://jsonapi.org/format/#document-resource-object-linkage.
        """

        return {'id': target['id'],
                'type': target['type'],
                'href': fmt_resource_url(target['id'])}


class UploadModel:
    def __init__(self, name, acceptable, *, db):
        self.acceptable = acceptable
        self.name = name
        self.db = db
        self.writeable = True
        self.is_upload = True
        self.is_array = False
        self.is_dict = False

    async def sanitize(self, data):
        assert False, 'this should not be called'

    async def render(self, id, data):
        return data


class AttributeModel:
    def __init__(self, name, schema, *, db):
        try:
            validate(schema, jsonschema.Draft4Validator.META_SCHEMA)
        except ValidationError as err:
            raise ValueError('invalid schema for %s: %s' % (name, err.message))
        self.schema = schema

        self.name = name
        self.db = db

        self.writeable = True
        self.is_upload = False
        self.is_array = False
        self.is_dict = False

    async def sanitize(self, data, check_consistency=True):
        """Verify an attribute value and return it's content."""

        try:
            validate(data, self.schema)
        except ValidationError as err:
            raise BadAttrError(key=self.name, err=err.message)
        return data

    async def render(self, id, data):
        return data


class RelationshipModel:
    META_SCHEMA = {
        'anyOf': [
            {'type': 'object',
             'properties': {
                 'type': {'type': 'string', 'pattern': '^relationship$'},
                 'arity': {'type': 'string', 'pattern': '^(to-one|to-many|keyed)$'},
                 'targets': {'anyOf': [
                     {'type': 'string'},
                     {'type': 'array', 'items': {'type': 'string'}}]},
             },
             'required': ['type', 'arity'],
             'additionalProperties': False},
            {'type': 'object',
             'properties': {
                 'type': {'type': 'string', 'pattern': '^relationship$'},
                 'arity': {'type': 'string', 'pattern': '^auto$'},
                 'pred-type': {'anyOf': [
                     {'type': 'string'},
                     {'type': 'array', 'items': {'type': 'string'}}]},
                 'pred-relationship': {'type': 'string'},
             },
             'required': ['type', 'arity', 'pred-type', 'pred-relationship'],
             'additionalProperties': False}
        ]
    }

    TO_ONE_SCHEMA = {
        'type': 'object',
        'properties': {
            'data': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'pattern': '^%s$' % UUID_RE},
                    'type': {'type': 'string', 'format': 'uri'},
                },
                'required': ['id'],
            },
        },
        'required': ['data'],
    }

    TO_MANY_SCHEMA = {
        'type': 'object',
        'properties': {
            'data': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string', 'pattern': '^%s$' % UUID_RE},
                        'type': {'type': 'string', 'format': 'uri'},
                    },
                    'required': ['id'],
                },
            },
        },
        'required': ['data'],
    }

    KEYED_SCHEMA = {
        'type': 'object',
        'properties': {
            'data': {
                'type': 'object',
                'patternProperties': {
                    '.*': {
                        'type': 'object',
                        'properties': {
                            'id': { 'type': 'string', 'pattern': '^%s$' % UUID_RE },
                            'type': { 'type': 'string', 'format': 'uri' },
                        },
                        'required': ['id'],
                    }
                }
            },
        },
        'required': ['data'],
    }

    def __init__(self, name, schema, *, db):
        try:
            validate(schema, RelationshipModel.META_SCHEMA)
        except ValidationError:
            raise ValueError('invalid schema for relationship %s' % name)
        self.arity = schema['arity']
        if self.arity in ('to-one', 'to-many', 'keyed'):
            self.link_model = LinkageModel(schema.get('targets'), db=db)
        else:  # self.arity == 'auto'
            self.pred_type = schema['pred-type']
            self.pred_rel = schema['pred-relationship']

        self.name = name
        self.db = db

        self.writeable = self.arity != 'auto'
        self.is_upload = False
        self.is_array = self.arity == 'to-many'
        self.is_dict = self.arity == 'keyed'

    async def sanitize(self, data, check_consistency=True):
        """Verify the relationship object and return its internal format."""

        if self.arity == 'to-one':
            try:
                validate(data, RelationshipModel.TO_ONE_SCHEMA)
            except ValidationError as err:
                raise BadRelError(key=self.name, err=err.message)
            if check_consistency:
                return await self.link_model.sanitize(data['data'])
            else:
                return {'id': data['data']['id']}

        elif self.arity == 'to-many':
            try:
                validate(data, RelationshipModel.TO_MANY_SCHEMA)
            except ValidationError as err:
                raise BadRelError(key=self.name, err=err.message)
            if check_consistency:
                links = []
                for link in data['data']:
                    links.append(await self.link_model.sanitize(link))
                return links
            else:
                return [{'id': link['id']} for link in data['data']]

        elif self.arity == 'keyed':
            try:
                validate(data, RelationshipModel.KEYED_SCHEMA)
            except ValidationError as err:
                raise BadRelError(key=self.name, err=err.message)
            if check_consistency:
                links = {}
                for (k, l) in data['data'].items():
                    links[k] = await self.link_model.sanitize(l)
                return links
            else:
                return {k: {'id': v['id']} for (k, v) in data['data'].items()}

        else:  # self.arity == 'auto'
            raise BadRelError('cannot write automatic relationship {key}',
                              key=self.name)

    async def render(self, id, link=None):
        """Render the relationship object.

        See https://jsonapi.org/format/#document-resource-object-relationships.
        """

        if self.arity == 'to-one':
            if link is None:
                data = None
            else:
                data = self.link_model.render(link)

        elif self.arity == 'to-many':
            data = [self.link_model.render(l) for l in link]

        elif self.arity == 'keyed':
            data = {k: self.link_model.render(v) for (k, v) in link.items()}

        else:  # self.arity == 'auto'
            cursor = self.db._db.resources.find(
                {'type': self.pred_type,
                 'body.%s.id' % self.pred_rel: id},
                {'_id': 1, 'type': 1})
            data = []
            async for hit in cursor:
                data.append({'id': hit['_id'],
                             'type': hit['type'],
                             'href': fmt_resource_url(hit['_id'])})

        return {'self': fmt_relationship_url(id, self.name),
                'data': data}
