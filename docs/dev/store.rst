***
API
***

The tozti core provides an API to perform operations on the database prefixed
with ``/api/store``. This API is largely inspired by jsonapi_ so you are
encouraged to go take a look at their specification.

Error format
============

If a request raised an error, the server will send back a response with status code ``500``, ``404`` or ``400``. This response might send back a json object with an entry ``errors`` containing a list of json objects with the following properties:

``code``
    The name of the error

``status``
    Status code of the error

``title``
    Short description of the error

``detail``
    More about this error. This entry might not be present.

``traceback``
    Traceback of the error. This entry might not be present.

Concepts and Datastructures
===========================

.. _resource object:

Resources
---------

Resources and `resource objects`_ are the main concept of the store API. A
resource is what we would call an entity in SQL lang or hypermedia in web lang.
A *resource object* is represented as a json object with the following
properties:

``id``
   An UUIDv4_ which uniquely identifies a resource.

``type``
   The name of a `type object`_.

``attributes``
   An arbitrary JSON object where each attribute is constained by the
   type of the resource.

``relationships``
   A JSON object where the keys are relationship names (just strings) and
   values are `relationship objects`_.

``meta``
   A JSON object containing some metadata about the resource. For now it
   only contains ``created`` and ``last-modified`` which are two
   self-explanatory dates in ISO 8601 format (UTC timezone).


.. _relationship objects:

Relationships
-------------

A relationship is a way to create a directed and tagged link between two
resources. Relationships can be *to-one* (resp. *to-many*) in which case
they link to one (resp. a sequence) of other resources. Practicaly, a
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

We remind that the api is quite similar to what jsonapi_ proposes.
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

A warrior has a name and a certain quantity of honor. He also possesses a weapon, and can be the (proud) owner of several cats (or no cats).


Fetching an object
------------------

To fetch an object, you must execute a ``GET`` request on ``/api/store/resources/{id}`` where ``id`` is the ``ID`` of the ressource.

Error code:
    - ``404`` if ``id`` corresponds to no known objects.
    - ``400`` if an error occured when processing the object (for exemple, one of the object linked to it doesn't exists anymore in the database).
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `resource object`_ under JSON format.

Exemple:
    Suppose that an object of type ``user`` and id ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. Then::
        
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
------------------

To create an object, you must execute a ``POST`` request on ``/api/store/resources`` where the body is a JSON object representing the object you want to send. The object must be encapsulated inside a `data` entry.  

Error code:
    - ``404`` if one of the object targetted by a relationship doesn't exists
    - ``400`` if an error occured when processing the object. For exemple, if the json object which was sended is malformated, or if the body of the request is not JSON..
    - ``200`` if the request was successful.

Returns:
    If the request is successful, the server will send back a `resource object`_ under JSON format.

Exemple:
    Suppose that an object of type ``user`` and id ``a0d8959e-f053-4bb3-9acc-cec9f73b524e`` exists in the database. Then::
        
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



.. _jsonapi: http://jsonapi.org/
.. _resource objects: http://jsonapi.org/format/#document-resource-objects
.. _UUIDv4: https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)
.. _jsonapi rel: http://jsonapi.org/format/#document-resource-object-relationships
.. _JSON Schema: http://json-schema.org/
