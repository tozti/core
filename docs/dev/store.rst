***
API
***

The tozti core provides an API to perform operations on the database prefixed
with ``/api/store``. This API is largely inspired by `JSON API`_ so you are
encouraged to go take a look at their specification.

Error format
============

The format of the errors follows `JSON API errors`_. If a request raised an
error, the server will send back a response with status code ``500``, ``404``
or ``400``. This response might send back a json object with an entry
``errors`` containing a list of json objects with the following properties:

``code``
    The name of the error

``status``
    Status code of the error

``title``
    Short description of the error

``detail``
    More about this error. This entry might not be present.

``traceback``
    Traceback of the error. This entry might not be present and is included
    only if tozti is launched in dev mode.

Concepts and Data Structures
============================

.. _resource object:

Resources
---------

Resources and `resource objects`_ are the main concept of the store API. A
resource is what we would call an entity in SQL or hypermedia on the web.
A *resource object* is represented as a json object with the following
properties:

``id``
   An UUIDv4_ which uniquely identifies a resource.

``type``
   The name of a `type object`_.

``attributes``
   An arbitrary JSON object where each attribute is constrained by the
   type of the resource.

``relationships``
   A JSON object where the keys are relationship names (just strings) and
   values are `relationship objects`_.

``meta``
   A JSON object containing some metadata about the resource. For now it
   only contains ``created`` and ``last-modified`` which are two
   self-explanatory dates in ISO 8601 format (UTC time zone).


.. _relationship objects:
.. _relationship object:

Relationships
-------------

A relationship is a way to create a directed and tagged link between two
resources. Relationships can be *to-one* (resp. *to-many*) in which case
they link to one (resp. a sequence) of other resources. Practically, a
*resource object* is a JSON object with the following properties (beware,
here we diverge a little from the `JSON API spec <jsonapi rel>`_):

``self``
   An URL pointing to the current relationship object. This URL can be
   used to operate on this relationship.

``data``
   In the case of a *to-one* relationship, this is a *linkage object*, in the
   case of a *to-many* relationship, this is an array of *linkage objects*.

Linkages are simply pointers to a resource. They are JSON objects with three
properties:

``id``
   The ID of the target resource.

``type``
   The type of the target resource.

``href``
   An URL pointing to the target resource.


.. _type object:

Types
-----

A *type object* is simply a JSON object with the following properties:

``attributes``
    A JSON object where keys are allowed (and required) attribute names for
    resource objects and values are JSON Schemas. A `JSON Schema`_ is a
    format for doing data validation on JSON. For now we support the Draft-04
    version of the specification (which is the latest supported by the library
    we use).

``relationships``
    A JSON object where the keys are allowed (and required) relationship names
    and keys are relationship description objects.

Relationship description objects are of 2 kinds, let's start with the simple
one:

``arity``
   Either ``"to-one"`` or ``"to-many"``, self-explanatory.

``type``
   This property is optional and can be used to restrict what types the targets
   of this relationship can be. It can be either the name of a type object or
   an array of names of allowed type objects.

The other kind of relationship description exists because relationships are
directed. As such, because sometimes bidirectional relationships are useful, we
would want to specify that some relationship is the reverse of another one. To
solve that, instead of giving ``arity`` and ``type``, you may give
``reverse-of`` property is a JSON object with two properties: ``type`` (a type
URL) and ``path`` (a valid relationship name for that type). This will specify
a new *to-many* relationship that will not be writeable and automatically
filled by the Store engine. It will contain as target any resource of the given
type that have the current resource as target in the given relationship name.

Let's show an example, we will consider two types: users and groups.

::

   // http://localhost/types/user.json
   {
       "attributes": {
           "login": {"type": "string"},
           "email": {"type": "string", "format": "email"}
       },
       "relationships": {
           "groups": {
               "reverse-of": {
                   "type": "group",
                   "path": "members"
               }
           }
       }
   }

::

   // http://localhost/types/group.json
   {
       "attributes": {
           "name": {"type": "string"}
       },
       "relationships": {
           "members": {
               "arity": "to-many",
               "type": "user"
           }
       }
   }

Now when creating a user you cannot specify it's groups, but you can specify
members when creating (or updating) a given group and the system will
automagically take care of filling the ``groups`` relationship with the current
up-to-date content.


Endpoints
=========

We remind that the API is quite similar to what `JSON API`_ proposes.
In the following section, type ``warrior`` is the type defined as::

        'attributes': {
            'name': { 'type': 'string' },
            'honor': { 'type': 'number'}
        },
        'relationships': {
            "weapon": {
                "arity": "to-one",
                "type": "weapon",
            },
            "kitties": {
                "arity": "to-many",
                "type": "cat"
            }

        }

A warrior has a name and a certain quantity of honor. He also possesses a
weapon, and can be the (proud) owner of several cats (or no cats).


Resources
---------

Fetching an object
^^^^^^^^^^^^^^^^^^

To fetch an object, you must execute a ``GET`` request on
``/api/store/resources/{id}`` where ``id`` is the ``ID`` of the resource.

Error code:
   - ``404`` if ``id`` corresponds to no known objects.
   - ``400`` if an error occurred when processing the object (for example, one of the object linked to it doesn't exists anymore in the database).
   - ``200`` if the request was successful.

Returns:
   If the request is successful, the server will send back a `resource object`_ under JSON format.

Example:
   Suppose that an object of type ``warrior`` and id ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. Then::

        >> GET /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e
        200
        {
           'data':{
              'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
              'type':'warrior',
              'attributes':{
                 'name':'Pierre',
                 'honor': 9000
              },
              'relationships':{
                 'self':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/self',
                    'data':{
                       'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
                       'type':'warrior',
                       'href':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e'
                    }
                 },
                 'weapon':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data':{
                       'id':'1bb2ff78-cefb-4ce1-b057-333f5baed577',
                       'type':'weapon',
                       'href':'/api/store/resources/1bb2ff78-cefb-4ce1-b057-333f5baed577'
                    }
                 },
                 'kitties':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data':[{
                       'id':'6a4d05f1-f04a-4a94-923e-ad52a54456e6',
                       'type':'cat',
                       'href':'/api/store/resources/6a4d05f1-f04a-4a94-923e-ad52a54456e6'
                    }]
                 }
              },
              'meta':{
                 'created':'2018-02-05T23:13:26',
                 'last-modified':'2018-02-05T23:13:26'
              }
           }
        }

Creating an object
^^^^^^^^^^^^^^^^^^

To create an object, you must execute a ``POST`` request on
``/api/store/resources`` where the body is a JSON object representing the
object you want to send. The object must be encapsulated inside a `data` entry.

Error code:
    - ``404`` if one of the object targeted by a relationship doesn't exists
    - ``400`` if an error occurred when processing the object. For example, if
      the json object which was sended is malformated, or if the body of the
      request is not JSON.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `resource
    object`_ under JSON format.

Example:
    Suppose that an object of type ``warrior`` and id
    ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. Then::

        >> POST /api/store/resources {'data': {'type': 'warrior', 
                        'attributes': {'name': Pierre, 'honor': 9000}, 
                        'relationships': {
                            'weapon': {'data': {'id': <id_weapon>}}, 
                            'kitties': {'data': [{'id': <kitty_1_id>}]}
                        }}}
        200
        {
           'data':{
              'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
              'type':'warrior',
              'attributes':{
                 'name':'Pierre',
                 'honor': 9000
              },
              'relationships':{
                 'self':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/self',
                    'data':{
                       'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
                       'type':'warrior',
                       'href':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e'
                    }
                 },
                 'weapon':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data':{
                       'id':'1bb2ff78-cefb-4ce1-b057-333f5baed577',
                       'type':'weapon',
                       'href':'/api/store/resources/1bb2ff78-cefb-4ce1-b057-333f5baed577'
                    }
                 },
                 'kitties':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data': [{
                       'id':'6a4d05f1-f04a-4a94-923e-ad52a54456e6',
                       'type':'cat',
                       'href':'/api/store/resources/6a4d05f1-f04a-4a94-923e-ad52a54456e6'
                    }]
                 }
              },
              'meta':{
                 'created':'2018-02-05T23:13:26',
                 'last-modified':'2018-02-05T23:13:26'
              }
           }
        }

Editing an object
^^^^^^^^^^^^^^^^^^

To edit an object, you must execute a ``PATCH`` request on
``/api/store/resources/{id}`` where ``id`` is the ID you want to update. The
body of the request must be a JSON object representing the change you want to
operate on the object. The object must be encapsulated inside a `data` entry.
Remark: you don't need to provide every entries.

Error code:
    - ``404`` if ``id`` corresponds to no known objects.
    - ``400`` if an error occurred when processing the object. For example, if
      the json object which was sended is malformated, or if the body of the
      request is not JSON.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `resource
    object`_ under JSON format representing the object (after changes are
    applied).

Example:
    We suppose the object with id ``a0d8959e-f053-4bb3-9acc-cec9f73b524e``
    exists in the database. Then::

        >> PATCH /api/store/resources {'data': {'type': 'warrior', 
                        'attributes': {'name': Luc}, 
                        'relationships': {
                            'weapon': {'data': {'id': <id_weapon_more_powerfull>}}, 
                        }}}
        200
        {
           'data':{
              'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
              'type':'warrior',
              'attributes':{
                 'name':'Luc',
                 'honor': 9000
              },
              'relationships':{
                 'self':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/self',
                    'data':{
                       'id':'a0d8959e-f053-4bb3-9acc-cec9f73b524e',
                       'type':'warrior',
                       'href':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e'
                    }
                 },
                 'weapon':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data':{
                       'id':'<id_weapon_more_powerfull>',
                       'type':'weapon',
                       'href':'/api/store/resources/<id_weapon_more_powerfull>'
                    }
                 },
                 'kitties':{
                    'self':'/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/friend',
                    'data': [{
                       'id':'6a4d05f1-f04a-4a94-923e-ad52a54456e6',
                       'type':'cat',
                       'href':'/api/store/resources/6a4d05f1-f04a-4a94-923e-ad52a54456e6'
                    }]
                 }
              },
              'meta':{
                 'created':'2018-02-05T23:13:26',
                 'last-modified':'2018-02-05T23:13:26'
              }
           }
        }


Deleting an object
^^^^^^^^^^^^^^^^^^

To delete an object, you must execute a ``DELETE`` request on
``/api/store/resources/{id}`` where ``id`` is the ID you want to update.
Remark: you don't need to provide every entries.

Error code:
    - ``404`` if ``id`` corresponds to no known objects.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back an empty JSON
    object.

Example:
    We suppose the object with id ``a0d8959e-f053-4bb3-9acc-cec9f73b524e``
    exists in the database. Then::

        >> DELETE /api/store/resources
        200
        {}


Relationships
-------------

In the same way that you can act on resources, you can also act on
relationships.

Fetching a relationship
^^^^^^^^^^^^^^^^^^^^^^^

To fetch a relationship, you must execute a ``GET`` request on
``/api/store/resources/{id}/{rel}`` where ``id`` is the ID of the resource
possessing the relationship you want to access, and ``rel`` the name of the
relationship.

Error code:
    - ``404`` if ``id`` corresponds to no known objects or ``rel`` is an
      invalid relationship name.
    - ``400`` if an error occurred when processing the object.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `relationship
    object`_ under JSON format.

Example:
    Suppose that an object of type ``warrior`` and id
    ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. Then::

        >> GET /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties", "data": [{
                    "id": "93b41bf0-73e8-4b37-b2b9-d26d758c2539", 
                    "type": "cat", 
                    "href": "/api/store/resources/93b41bf0-73e8-4b37-b2b9-d26d758c2539"
                }, {
                    "id": "dff2b520-c3b0-4457-9dfe-cb9972188e48", 
                    "type": "cat", 
                    "href": "/api/store/resources/dff2b520-c3b0-4457-9dfe-cb9972188e48"
                }]
            }
        }

    ::

        >> GET /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/weapon
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/weapon", "data": {
                    "id": "34078dd5-516d-42dd-816d-6fbfd82a2da9",
                    "type": "weapon", 
                    "href": "/api/store/resources/34078dd5-516d-42dd-816d-6fbfd82a2da9"
                }
            }
        }



Updating a relationship
^^^^^^^^^^^^^^^^^^^^^^^

To update a relationship (which is not an automatic relationship), you must
execute a ``PUT`` request on ``/api/store/resources/{id}/{rel}`` where ``id``
is the ID of the resource possessing the relationship you want to access, and
``rel`` the name of the relationship. The content of your request is a JSON
object containing:

- for a ``to-one`` relationship the ID of the new target
- for a ``to-many`` relationship several IDs representing the new targets

Error code:
    - ``404`` if ``id`` corresponds to no known objects or ``rel`` is an
      invalid relationship name.
    - ``400`` if an error occurred when processing the object.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `relationship
    object`_ under JSON format.

Example:
    Suppose that an object of type ``warrior`` and id
    ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. We also
    suppose that its relationship ``kitties`` possesses two targets having id
    ``<id1>`` and ``<id2>``. The relationship ``weapon`` targets
    ``<id_sword>``. Then::

        >> PUT /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties {'data': [{'id': <id3>}]}
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties", "data": [{
                    "id": <id3>, 
                    "type": "cat", 
                    "href": "/api/store/resources/<id3>"
                }]
            }
        }

    ::

        >> PUT /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/weapon {'data': {'id': <id_shotgun>}}
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/weapon", "data": [
                    "id": <id_shotgun>, 
                    "type": "weapon", 
                    "href": "/api/store/resources/<id_shotgun>"
                ]
            }
        }


Adding new targets to a relationship
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add new targets to a ``to-many`` relationship, you must execute a ``POST``
request on ``/api/store/resources/{id}/{rel}`` where ``id`` is the ID of the
resource possessing the relationship you want to access, and ``rel`` the name
of the relationship. The content of your request is a JSON object containing
the ids of the objects you want to add to the relationship.

Error code:
    - ``404`` if ``id`` corresponds to no known objects or ``rel`` is an
      invalid relationship name.
    - ``403`` if the relationship is not a too-many relationship
    - ``400`` if an error occurred when processing the object.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `relationship
    object`_ under JSON format.

Example:
    Suppose that an object of type ``warrior`` and id
    ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. We also
    suppose that its relationship ``kitties`` possesses one targets having id
    ``<id1>``. Then::

        >> POST /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties {'data': [{'id': <id2>}, {'id': <id3>}]}
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties", "data": [{
                    "id": <id1>, 
                    "type": "cat", 
                    "href": "/api/store/resources/<id1>"
                }, {
                    "id": <id2>, 
                    "type": "cat", 
                    "href": "/api/store/resources/<id2>"
                }, {
                    "id": <id3>, 
                    "type": "cat", 
                    "href": "/api/store/resources/<id3>"
                }]
            }
        }


Deleting a relationship
^^^^^^^^^^^^^^^^^^^^^^^

To fetch some targets from a ``to-many`` relationship, you must execute a
``DELETE`` request on ``/api/store/resources/{id}/{rel}`` where ``id`` is the
ID of the resource possessing the relationship you want to access, and ``rel``
the name of the relationship. The content of your request is a JSON object
containing the ids of the objects you want to remove from the relationship.

Error code:
    - ``404`` if ``id`` corresponds to no known objects or ``rel`` is an
      invalid relationship name.
    - ``403`` if the relationship is not a too-many relationship
    - ``400`` if an error occurred when processing the object.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `relationship
    object`_ under JSON format.

Example:
    Suppose that an object of type ``warrior`` and id
    ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. We also
    suppose that its relationship ``kitties`` possesses three targets having
    ids ``<id1>``, ``<id2>`` and ``<id3>``. Then::

        >> DELETE /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties {'data': [{'id': <id1>}, {'id': <id3>}]}
        200
        {
            "data": {
                "self": "/api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/kitties", "data": [{
                    "id": <id2>, 
                    "type": "cat", 
                    "href": "/api/store/resources/<id2>"
                }]
            }
        }

    ::

        >> DELETE /api/store/resources/a0d8959e-f053-4bb3-9acc-cec9f73b524e/weapon
        403
        {
            "errors": [{
                "code": "BAD_RELATIONSHIP", 
                "title": "a relationship is invalid", 
                "status": "403", 
                "detail": "to-one relationships cannot be deleted"
            }]
        }


Types
-----

Fetching all instances of a given type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To fetch all instances of a given type ``<type>``, you must execute a
``GET`` request on ``/api/store/by-type/<type>``.

Error code:
    - ``404`` if the type doesn't exists
    - ``400`` if an error occurred when processing the object.
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a list of linkage 
    objects encapsulated under a `data` entry. Each linkage object points toward
    a ressources having type ``<type>``

Example:
    To fetch every ``warrior`` present inside our ``store``, you can proceed as
    following::

        >> GET /api/store/by-type/warrior
        200
        {
            "data": [
            {
                "id": "60f1677b-2bbb-4fd9-9a7a-3a20dbf7b5af", 
                "type": "core/user", 
                "href": "/api/store/resources/60f1677b-2bbb-4fd9-9a7a-3a20dbf7b5af"
            }, {
                "id": "605ab4bc-172b-416e-8a13-186cf3cd1e2e", 
                "type": "core/user", 
                "href": "/api/store/resources/605ab4bc-172b-416e-8a13-186cf3cd1e2e"
            }]
        }

Remark:
    Most of the time, type names are under this form: ``<ext-name>/<type-name`` where
    ``<ext-name>`` is the name of the extension defining the type ``<type-name>``. To 
    fetch of instances of this type, send a ``GET`` request on ``/api/store/by-type/<ext-name>/<type-name>``.


.. _JSON API: http://jsonapi.org/
.. _resource objects: http://jsonapi.org/format/#document-resource-objects
.. _UUIDv4: https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)
.. _jsonapi rel: http://jsonapi.org/format/#document-resource-object-relationships
.. _JSON Schema: http://json-schema.org/
.. _JSON API errors: http://jsonapi.org/format/#error-objects 
