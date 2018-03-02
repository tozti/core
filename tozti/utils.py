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


from json import JSONEncoder, dumps
from datetime import datetime
from uuid import UUID

from aiohttp.web import json_response as _json_response
import jsonschema
from jsonschema.exceptions import ValidationError


class RouteDef:
    """Definition of a route.

    The method :meth:`get`, :meth:`post`, :meth:`put`, etc can be used as
    decorators to specify the handler for the given HTTP method.
    """

    def __init__(self, path, name=None):
        self._path = path
        self._name = name
        self._routes = {}
        self._prefix = ''

    def register(self, app):
        """Add all our routes to the given `aiohttp.web.Application`."""

        route = app.add_resource(self._path, name=self._name)
        route.add_prefix(self._prefix)
        for m, h in self._routes.items():
            route.add_route(m, h)

    def route(self, *meth):
        """Decorator (with arguments) used to specify HTTP handler."""

        def decorator(handler):
            for m in meth:
                self._routes[m] = handler
            return handler
        return decorator

    def get(self, handler):
        """Decorator used to specify ``GET`` method handler."""

        self._routes['GET'] = handler
        return handler

    def post(self, handler):
        """Decorator used to specify ``GET`` method handler."""

        self._routes['POST'] = handler
        return handler

    def put(self, handler):
        """Decorator used to specify ``PUT`` method handler."""

        self._routes['PUT'] = handler
        return handler

    def patch(self, handler):
        """Decorator used to specify ``PATCH`` method handler."""

        self._routes['PATCH'] = handler
        return handler

    def delete(self, handler):
        """Decorator used to specify ``DELETE`` method handler."""

        self._routes['DELETE'] = handler
        return handler

    def head(self, handler):
        """Decorator used to specify ``HEAD`` method handler."""

        self._routes['HEAD'] = handler
        return handler

    def options(self, handler):
        """Decorator used to specify ``OPTIONS`` method handler."""

        self._routes['OPTIONS'] = handler
        return handler

    def any(self, handler):
        """Decorator used to specify handler for every method."""

        self._routes['*'] = handler
        return handler


class RouterDef:
    """Handle route definitions.

    This object can be used as argument to
    :meth:`aiohttp.web.UrlDispatcher.add_routes`.

    Sample usage::

        router = RouterDef()
        route = router.add_route('/foo')

        @route.get
        def handle_get(req):
            return ...

    See `aiohttp`_ for more informations on resources and routing.

    .. _aiohttp: https://aiohttp.readthedocs.io/en/stable/web.html#resources-and-routes
    """

    def __init__(self):
        self._routes = []

    def add_route(self, path, name=None):
        """Add and return a route with given path to the router."""

        r = RouteDef(path, name=name)
        self._routes.append(r)
        return r

    def add_prefix(self, prefix):
        """Prefix every contained route."""

        for r in self._routes:
            r._prefix = prefix

    def __iter__(self):
        return iter(self._routes)


class ExtendedJSONEncoder(JSONEncoder):
    """JSON encoder handling `datetime.datetime` and `uuid.UUID`."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            super().default(obj)


def json_response(data, **kwargs):
    """Wrapper for `aiohttp.web.json_response` with extended JSON encoder."""

    fancy_dumps = lambda obj: dumps(obj, cls=ExtendedJSONEncoder)
    return _json_response(data, dumps=fancy_dumps, **kwargs)


def validate(inst, schema):
    """Validate data against a JsonSchema."""

    return jsonschema.validate(inst, schema, cls=jsonschema.Draft4Validator,
                               format_checker=jsonschema.FormatChecker())


def current_time():
    return datetime.utcnow().replace(microsecond=0)


class ConfigError(Exception):
    pass


class APIError(Exception):
    """Base class for API errors."""

    code = 'MISC_ERROR'
    title = 'error'
    status = 400

    def __init__(self, template=None, status=None, **kwargs):
        if template is not None:
            self.template = template
        if status is not None:
            self.status = status
        if hasattr(self, 'template'):
            args = (self.template.format(**kwargs),)
        else:
            args = ()

        super().__init__(*args)

    def to_response(self):
        """Create an `aiohttp.web.Response` signifiying the error."""

        error = {'code': self.code, 'title': self.title,
                 'status': str(self.status)}
        if len(self.args) > 0:
            error['detail'] = self.args[0]

        return json_response({'errors': [error]}, status=self.status)


class NotJsonError(APIError):
    code = 'NOT_JSON'
    title = "content type is not `application/vnd.api+json`"
    status = 406


class BadJsonError(APIError):
    code = 'BAD_JSON'
    title = 'json data is malformated'
    status = 400


class BadDataError(APIError):
    code = 'BAD_DATA'
    title = 'submitted data is invalid'
    status = 400


class BadMethodError(APIError):
    code = 'BAD_METHOD'
    title = 'HTTP method not allowed'
    status = 405


class NotAcceptableError(APIError):
    code = 'NOT_ACCEPTABLE'
    title = 'data has bad content type'
    status = 406
