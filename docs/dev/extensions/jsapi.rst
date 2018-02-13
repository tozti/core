********************
Using Tozti's JS api
********************


Defining routes on the client side
==================================

If you read :doc:`getting-started` you learned how to define new API endpoints.
But you might want that your extension also provide some endpoints on the 
client, to display a special page for example.

You can take a look at how the extension `vue-counter` of the `sample-extensions`_ 
repository uses this mechanism to define a counter reachable on ``<tozti>/counter``.

Tozti's extensions are using vue, so it is natural that we use ``vue-router`` in order
to define new routes.

Imagine you want to define a new 'page' displaying a component called ``Calendar`` that 
can be accessed on ``<tozti>/mycalendar``. Then, you must add the following lines in your
``index.js``::
    
    tozti.routes.unshift(
        { path: '/mycalendar', component: Calendar }
    )


Adding items in the menu bar
============================

An exemple can be found in the extension `add-menu-item` that can be found in the 
repository `sample-extensions`_.

Every extensions can add items in the sidebar. We will focus on what we call `menu items`:
items that are attached to tozti as a whole, not to a workspace.

The corresponding method allowing to do that is called ``tozti.addMenuItem``. 
Here are following examples of usage:

- Adding an item with the text 'item' associated with the route `target/`::

    tozti.addMenuItem('item', 'target/')

- Adding an item with the text 'item' associated with the route `target/` 
  and the icon 'nc-home-52'::

    tozti.addMenuItem('item', 'target/', 
                      props = {'icon': 'nc-home-52'}
                      )



.. _getting-started`_: [TODO put link]
.. _sample-extensions: https://github.com/tozti/sample-extensions
