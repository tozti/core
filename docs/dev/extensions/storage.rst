******************************
Communication with the storage
******************************

More often than not, the purpose of an extension is to define new types of resources,
and provide new interactions with them from the tozti interface.
For this purpose, tozti provides an easy way to define new types on the server-side,
and a generic client-side API to query the store from the frontend.



Defining new types of resources
===============================

For validation purposes, when you want to create a new type of resource in the store,
you need to specify how such a resource is structured.
This is done via **schemas**, similar to the JSONSchema specification.

New type schemas can be defined from an extension by providing a new entry called ``types``
in the ``MANIFEST`` of the extension.
This entry should be a dictionary, whose keys are the names of the new types, and values are
valid schemas.

Let's show how this works with a simple example, with our dummy extension.
We would like to define a new resource type called ``entity``, with attributes ``name`` and ``age``.
For the sake of it, let it also have a ``to-many`` relationship named ``friends``.

Therefore, our ``MANIFEST`` (defined in ``server.py``) should look like::

  MANIFEST = {
    'types': {

      'entity': {

        'attributes': {
          'name': { 'type': 'string' },
          'age': { 'type': 'integer' },
        },

        'relationships': {
          'friends': {
            'arity': 'to-many',
            'type': 'dummy-extension/entity',
          }
        }

      }

    }
  }

Note that in the rest of this documentation, extension-defined type names will be prefixed
by the name of the folder containing the extensions.
Assuming our extension lives in a folder called ``dummy-extension`` in the ``extensions`` folder of
our main tozti instance, the newly defined type will now be referred as ``dummy-extensions/entity``.
This also applies to the core ``types``. For example, we provide by default types ``core/user``, and ``core/group``.
That is why in the relationship ``friends`` of the type we just defined, we refer to ``dummy-extensions/entity``.

Further information on type schemas and how the storage uses them can be found in the documentation specific to the storage. (TODO: add link).


Accessing the store from the JS API
===================================


Resources
^^^^^^^^^

Now that we have registered a new type for resources in the store, we would like to have the ability to interact with such resources. tozti provides a generic API for this end, under the ``tozti.store`` namespace.


Getting a resource
------------------

When you have the *uuid* of a resource, you can get its data from the store by using the ``get`` method:

.. code-block:: javascript

   tozti.store.get(uuid)

This method returns a javascript **promise**, that resolves to the resource object, or rejects to the HTTP response object.

For exemple, assuming the variable ``uuid`` contains the uuid of a resource of type ``dummy-extension/entity``,
we can print the name of said entity by doing:

.. code-block:: javascript

   tozti.store
     .get(uuid)
     .then(resource => {
       console.log(resource.attributes.name)
     })
     .catch(response => {
       console.error('An error occured while fetching the resource.')
     })

.. danger::
   You should never write to the resource objects given by the ``tozti.store`` methods, ever.
   Think of them as readonly objects.
   If you want to update a resource, see ``tozti.store.update`` introduced below.


Creating a new resource
-----------------------

To populate the store from the client-side, you have the ability to create new resources and send them
to the server store. First define a new resource object:

.. code-block:: javascript

   let resource = {
     type: 'dummy-extension/entity',
     attributes: {
       name: 'Some Entity',
       age: 15,
     }
   }

The only required field is the ``type`` field, for the storage to know what you are trying to create.
Note that the associated ``type`` schema may itself require you to specify other fields.

Then, you can create the resource and send it to the store with the ``create`` method:


.. code-block:: javascript

   tozti.store.create(resource)


This method also returns a javascript **promise**, that resolves to the full store resource object, or rejects to the HTTP response object.
The resolved resource is a fully defined store resource, so it contains a ``meta`` field with meta information, and ``attributes`` and ``relationships`` objects in accordance with the resource type.
It also has an ``id`` field, which contains the uuid of the resource inside the remote store.

.. code-block:: javascript

   tozti.store
     .create(resource)
     .then(res => {
       console.log('The resource was created.')
       console.log(res.id)
     })
     .catch(response => {
       console.error('An error occured while creating the resource.')
     })


Updating a resource
-------------------

Another usual operation is updating an existing resource.
This is done via the ``update`` method.

First, you need to define a resource object containing only the items that you want to see updated,
and at the very least an ``id``.

.. code-block:: javascript

   let changes = {
     id: 'some-resource-id',
     attributes: {
       name: 'A new name for the entity',
     }
   }

Then, using the ``update`` method will try to apply the changes to the server:

.. code-block:: javascript

   tozti.store.update(changes)


Again, this method returns a javascript **promise**, that resolves to the full store resource object, with the applied changes.

.. code-block:: javascript

   tozti.store
     .update(changes)
     .then(resource => {
       console.log(resource.attributes.name)
       // expected output: A new name for the entity
     })
     .catch(response => {
       console.error('An error occured while updating the resource.')
     })


Deleting a resource
-------------------

Finaly, to delete a resource from the store, one can use the ``delete`` method.
This method takes a resource object as a parameter, whose only needed field is ``id``.
(The fact that it takes a resource object is for convenience only).

Assuming, ``uuid`` contains some entity id, and ``resource`` contains a complete resource object coming from the store,
it can be used like this:

.. code-block:: javascript

   tozti.store.delete({ id: uuid })
   tozti.store.delete(resource)

As expected, this method also returns a **promise**, which resolves to an empty object when the deletion was successful, or to the HTTP response in the eventuality of an error.



Relationships
^^^^^^^^^^^^^

If some resource has a relationship, then in the resource object returned from the store, the associated relationship field only contains a *linkage*, or an array of *linkages*.

(Recall that a *linkage* is simply an object referring to a resource, containing fields ``type`` and ``id``, plus additional data)

tozti provides helper functions for fetching the entire data of a relationship, and updating it, in the ``tozti.store.rels`` namespace.


Getting the resources of a relationship
---------------------------------------

To get all the resources pointed by a relationship, use the ``rels.fetch`` method.
It takes as a parameter a relationship object coming from some resource object returned by the store,
and returns a Promise.

This promise either resolves to a single resource object when the relationship is ``to-one``, or to an array of resource objects when the relationship is ``to-many``. 

This promise is rejected if any of the resources contained in the relationship cannot be accessed from the server.
For this reason, and for a better UX experience, it is preferred to not use ``fetch`` but instead defer the responsability of loading contained resources to individual components, that can display errors more intuitively. (See: part on using the store from Vue components, further down on the same page)


Assume that we have a resource ``resource`` of type ``dummy-extension/entity``, then we can get all resources contained in the ``friends`` relationship by doing:

.. code-block:: javascript

   tozti.store.rels
     .fetch(resource.relationships.friends)
     .then(friends => {
       // log the name of every friend in the relationship
       friends.forEach(friend => {
         console.log(friend.attributes.name)
       })
     })
     .catch(response => {
       console.error('An error occured while fetching some entities of the relationship')
     })


Appending resources to a `to-many` relationship
-----------------------------------------------

``rels.add`` allows you to add some resource to a relationship.
Its first parameter is a relationship object.
All the other arguments will be interpreted as linkages to be added to the relationship.
It returns a promise resolving to the new relationship object.
Note that the original relationship object is actually mutated to correspond to the new relationship data.
The linkages provided only need to define an ``id`` field.

Assuming we have two resources ``pomme``, ``poire``, ``abricot`` of type ``dummy-extensions``,
adding ``poire`` and ``abricot`` to the relationship ``friends`` of resource ``pomme`` is done like this:

.. code-block:: javascript

   tozti.store.rels
     .add(pomme.relationships.friends, { id: poire.id }, abricot)

If some linkages already exist inside the relationship, they will not be added twice but the promise will still resolve correctly to the relationship object.


Removing resources from a `to-many` relationship
------------------------------------------------

``rels.delete`` does the exact opposite of ``rels.add``: it allows you to remove some resources from a relationship.
It takes a relationship object as first parameter, and any other argument will be interpreted as a linkage.
It returns a promise resolving to the new relationship object.

Again, the original relationship object is actually mutated to correspond to the new relationship data.
Linkages provided only need to hold an ``id`` field.

Using the same exemple as before, we now want to remove ``poire`` and ``abricot`` from the relationship ``friends`` of resource ``pomme``:

.. code-block:: javascript

   tozti.store.rels
     .delete(pomme.relationships.friends, poire, { id: abricot.id })

If some linkages do not exist inside the relationship, they will simply be ignored, and the promise will still resolve correctly to the relationship object.


Updating a relationship
-----------------------

Unimplemented yet.
This will be added soon.



Accessing data from Vue components
==================================

A nice feature that was purposefully ignored earlier, is the fact that the JS API keeps a local version of the store.
What this means is that when someone uses ``tozti.store.get`` with the id of a resource that was already fetched somewhere else, the promise will immediately resolve to **the same cached resource object**.

Likewise, every operation sent to the remote storage will be applied to the cached version of the resource, if it exists. For example, ``tozti.store.update`` will locally mutate the cached target resource to sync with the server version.

This is especially useful in that it enables reactivity without even having to think about it. Simply update a resource and the changes will be seen everywhere the resource is being used, on the frontend, without actually having to request the data from the server again.

Below, we will look at how one can actually use the store API to fetch data inside Vue components.


Resource components
^^^^^^^^^^^^^^^^^^^

Usually, it is good to use specific components to display a single resource. Be it inside a list of items, or a single page displaying information about the resource, working with individual components that care about a single resource at the time is easier to reason about and compose into more involved components.

Let's define a component called ``EntityView`` that will display information about one resource.
For the component to know which resource it is being associated with, we need to give it an ``id``, through props.
As soon as the component is being used (i.e mounted), we want the component to fetch the necessary data from the store.
Finally, as long as the data request is being processed, we simply cannot show any data, so we need to make sure
that the loading is explicit inside the component.


This would give something similar in the vein of:

.. caution::
   This is given as an exemple,
   but we would prefer you using ``resourceMixin``, introduced right after.

.. code-block:: html

   <template>
     <div>
       <p v-if="resource">
         Name: {{ resource.attributes.name }} <b>
         Age:  {{ resource.attributes.name }}
       </p>
       <p v-else>
         The resource is being loaded.
       </p>
     </div>
   </template>
   <script>
     export default {
       props: {
         id: {
           type: String
         }
       },

       data() {
         return {
           resource: null
         }
       },

       beforeMounted() {
         tozti.store.get(this.id)
           .then(resource => {
             this.resource = resource
           })
       }
     }
   </script>

Then the component can be used with ``<entity-view :id="some-resource-id"></entity-view>``.

This should work properly: we query the data when the component is mounted, and conditionally display the content once the resource has been returned.
However, making this work reliably is more involved, since components can be reused and repurposed freely by Vue.

To make it easier for developers to define this kind of components, we provide a default mixin:

.. code-block:: html

   <template>
     <div>
       <p v-if="!loading">
         Name: {{ resource.attributes.name }} <b>
         Age:  {{ resource.attributes.name }}
       </p>
       <p v-else>
         The resource is being loaded.
       </p>
     </div>
   </template>
   <script>
     import { resourceMixin } from 'tozti'
     
     export default {
       mixins: [ resourceMixin ]
     }
   </script>


This mixin defines two data fields:

- ``loading``, a boolean that indicates whether a data request is currently being processed.
- ``resource``, initially set to ``null``, that will contain the resource once it has been acquired.

Use this mixin as soon as it may be suitable!



Displaying relationships
^^^^^^^^^^^^^^^^^^^^^^^^

Using relationships inside Vue components is quite similar.
Here we will describe the common patterns related to **to-many** and **to-one** relationships.


to-many relationships
---------------------

When one wants to display the associated resources of some relationship,
the preferred pattern is to simply display a list of components, that will each be responsible for displaying a single resource of the relationship.
This allows for fine-grained error handling, when one of the resources no longer exists. In such a situation, the associated component can simply display an error message, without affecting the other components.

To react to relationship changes, you need to add the relationship ``data`` array inside the data of your main component, that will contain every linkage included in the relationship.

In our example, we assume that we are defining a global component, that displays a given ``dummy-extension/entity``'s friends:

.. code-block:: html

   <template>
     <div v-if="!loading">
       <entity-view v-for="friend in friends" :id="friend.id" :key="friend.id">
       </entity-view>
     </div>
   </template>
   <script>
     import { resourceMixin } from 'tozti'
     
     export default {
       mixins: [ resourceMixin ],

       computed: {
         friends() {
           // this.friends will contain an array of linkages
           // and will be computed when the main resource is finally ready
           return this.resource.relationships.friends.data
         }
       }

     }

   </script>

In this exemple, we defer the responsability of loading individual resources to the ``EntityView`` component defined earlier.
The relationship data array will be watched by Vue, therefore when the relationship is updated somewhere inside the client, the interface should be updated without needing further work.
