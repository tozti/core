# -*- coding: utf-8 -*-

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


from requests import Session


API = 'http://127.0.0.1:8080/api'


class APIError(Exception):
    def __init__(self, code, **kwargs):
        super().__init__(code, kwargs.values())
        self.code = code
        self.status = kwargs.get('status')
        self.detail = kwargs.get('detail')
        self.traceback = kwargs.get('traceback')

    def __str__(self):
        msg = self.code
        if self.status is not None:
            msg += ' [%s]' % self.status
        if self.detail is not None:
            msg += ': %s' % self.detail
        if self.traceback is not None:
            msg += '\n=== SERVER TRACEBACK ===\n%s' % self.traceback
        return msg


def check_call(meth, path, json=None, prefix=API, session=None):
    """Make an API call.

    Raises APIError in case the api returns an error. Raises JSONDecodeError
    if the response is not valid JSON.
    """

    if session is None:
        session = Session()

    resp = session.request(meth, prefix + path, json=json,
                            headers = { 'content-type': 'application/vnd.api+json' })

    ans = resp.json()
    if 'errors' in ans:
        raise APIError(**ans['errors'][0])
    return ans


## Resource endpoints

def resource_create(session=None, **kwargs):
    """Create and return a resource.

    You should pass `type`, `attributes` and optionally `relationships` as
    arguments.
    """

    ans = check_call('POST', '/store/resources', json={'data': kwargs}, session=session)
    return ans['data']


def resource_fetch(id, session=None):
    """Get a resource object by it's UUID."""

    ans = check_call('GET', '/store/resources/%s' % id, session=session)
    return ans['data']


def resource_update(id, session=None, **kwargs):
    """Partially update a resource.

    You can only change attributes and relationships.
    """

    ans = check_call('PATCH', '/store/resources/%s' % id,
                             json={'data': kwargs}, session=session)
    return ans['data']


def resource_delete(id, session=None):
    """Delete a resource by it's UUID."""

    check_call('DELETE', '/store/resources/%s' % id, session=session)


## Relationship endpoints

def relationship_get(id, rel, session=None):
    """Get a relationship."""

    return check_call('GET', '/store/resources/%s/%s' % (id, rel), session=session)


def relationship_update(id, rel, data, session=None):
    """Overwrite a relationship."""

    return check_call('PUT', '/store/resources/%s/%s' % (id, rel),
                      json={'data': data}, session=session)


def relationship_append(id, rel, data, session=None):
    """Append items to a to-many relationship."""

    return check_call('POST', '/store/resources/%s/%s' % (id, rel),
                      json={'data': data}, session=session)


def relationship_delete(id, rel, data, session=None):
    """Delete items from a to-many relationship."""

    return check_call('DELETE', '/store/resources/%s/%s' % (id, rel),
                      json={'data': data}, session=session)

def by_handle_get(handle, session=None):
    """Looks up an item by its handle."""

    return check_call('GET', '/store/by-handle/%s' % handle, session=session)

def by_handle_post(handle, data, session=None):
    """Redirects the given handle to point to a given id. Creates the handle if necessary"""

    return check_call('POST', '/store/by-handle/%s' % handle, json={'data': data}, session=session)

def by_handle_delete(handle, session=None):
    """Unassociates the handle from its target id."""

    return check_call('DELETE', '/store/by-handle/%s' % handle, session=session)

## Authentication endpoint
# uses session

def create_user(login, name, passwd, email, session=None):
    """Create an user."""

    return check_call('POST', '/auth/create_user',
                      json={'name':name, 'login':login,
                            'passwd':passwd, 'email':email},
                      session=session)

def login(login, passwd, session):
    """Log in."""

    return check_call('POST', '/auth/login',
                      json={'passwd':passwd, 'login':login},
                      session=session)
