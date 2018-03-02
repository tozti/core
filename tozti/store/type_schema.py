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


import jsonschema
from tozti.utils import validate, ValidationError


TYPE_SCHEMA = {
    'anyOf': [
        { 'type': 'string', 'format': 'uri' },
        { 'type': 'array', 'items': { 'type': 'string', 'format': 'uri' }  }
    ]
}

META_SCHEMA = {
    'type': 'object',
    'properties': {
        'attributes': {
            'type': 'object',
            'patternProperties': {
                '.*': jsonschema.Draft4Validator.META_SCHEMA,
            }
        },
        'relationships': {
            'type': 'object',
            'patternProperties': {
                '.*': {
                    'anyOf': [{
                        'type': 'object',
                        'properties': {
                            'reverse-of': {
                                'type': 'object',
                                'properties': {
                                    'type': TYPE_SCHEMA,
                                    'path': { 'type': 'string' },
                                },
                                'required': ['type', 'path'],
                            },
                        },
                        'required': ['reverse-of']
                    }, {
                        'type': 'object',
                        'properties': {
                            'arity': {
                                'type': 'string',
                                'pattern': '^(to-one|to-many)$',
                            },
                            'type': TYPE_SCHEMA
                        },
                        'required': ['arity'],
                    }]
                }
            }
        }
    },
    'additionalProperties': False,
    'required': ['attributes', 'relationships'],
}


class Schema:
    def __init__(self, raw):
        try:
            validate(raw, META_SCHEMA)
        except ValidationError as err:
            raise ValueError('invalid schema: %s' % err.message)

        self.attrs = raw['attributes']
        self.to_one = {}
        self.to_many = {}
        self.autos = {}
        for (rel, rel_def) in raw['relationships'].items():
            if 'reverse-of' in rel_def:
                self.autos[rel] = (rel_def['reverse-of']['type'],
                                   rel_def['reverse-of']['path'])
                continue

            if 'type' in rel_def:
                if isinstance(rel_def['type'], str):
                    types = {rel_def['type']}
                else:
                    types = set(rel_def['type'])
            else:
                types = None
            if rel_def['arity'] == 'to-one':
                self.to_one[rel] = types
            elif rel_def['arity'] == 'to-many':
                self.to_many[rel] = types
            else:
                raise AssertionError('BAD! Invalid schema after validation')
