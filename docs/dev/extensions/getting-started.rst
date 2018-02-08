***************
Getting Started
***************

Our first extension
===================

Let's see how to create a simple extension to *tozti*. Everything defined by an
extension lives inside the same folder, whose name is the name of the
extension.

Suppose we call it ``extension-name``. Browse to the ``extensions/`` folder and
proceed to create a folder ``extension-name``.  The only requirement for
*tozti* to recognize an extension is for this extension to provide a file
``server.py`` declaring a dictionnary ``MANIFEST``.  Thus a minimal definition
would be like so::

    MANIFEST = {}

Well done, you've just created your first extension!


Defining an API endpoint
========================

The previous extension currently does nothing. We will now see how to add new
API endpoints to the application.

At the moment our ``MANIFEST`` is empty. To declare new routes, we must import
some modules::

    from tozti.utils import RouterDef
    from aiohttp import web
    import logbook

* ``RouterDef`` allows us to define a new router and therefore new request
  handlers.
* ``web`` from ``aiohttp`` enables us to send back to the user simple
  responses.
* ``logger`` is a simple utility to pretty print information in the server
  logs.

We define a logger, which will enable us to output useful information to the console::
    
    logger = logbook.Logger("tozti-routing")

Then, we create an empty router::

    router = RouterDef()

And we add one endpoint to it. We call it ``hello_world``, and make it
accessible from the URL ``<tozti>/api/extension-name/hello_world``::

    hello_world = router.add_route('/hello_world')

Finally, we define how our extension should behave when this endpoint is
requested. In this example, we respond to ``GET`` requests on this endpoint
with some dummy text::

    @hello_world.get
    async def hello_world_get(req):
        logger.info("hello world")
        return web.Response(text='Hello world!')

Similar decorators are available for the usual HTTP methods:
``@hello_world.post``, etc.

Unfortunately, for now *tozti* still isn't aware of this new request handler we
just defined. This is where ``MANIFEST`` comes into use: We simply add the
router in the ``MANIFEST`` dict under the key ``router``::

    MANIFEST = {
        'router': router,
    }

In fact, ``MANIFEST`` is where we declare anything that *tozti* should be made
aware of.

And now, if you launch the server again, and visit the URL
``<tozti>/api/extension-name/hello_world``, your web browser should display a
blank web page with the text *"Hello world!"*. If you look in the server logs,
some ``hello world`` must have appeared.


Providing custom javascript to the tozti application
====================================================

If the previous paragraph showed how to serve content on specific URLs, this is
*not* how we modify the behavior of the *tozti* application. *tozti* is a
single-page app built with the framework **Vue.js**. Therefore if you want to
be able to interact with the application and define new interactions, you need
to be able to serve custom *javascript* code to the client.

As a convention, all static assets must be put inside a folder ``dist`` inside
your extension folder. Let's create a file called ``index.js`` inside
``extension-name/dist/``:

.. code-block:: javascript

  tozti.store.commit('registerWidget', {
    template: '<div class="uk-placeholder">A widget coming directly from our extension! :)</div>'
  })

As you might have guessed, we need to inform *tozti* of the existence of this
file, inside ``MANIFEST``::

  MANIFEST = {
    # ..
    'includes': ['index.js']
  }

Once again, start the server and visit the URL ``<tozti>/``. A new widget
should have appeared inside the Dashboard.

As stated below, adding CSS files in this ``includes`` list in exactly the same
fashion allows the inclusion of custom CSS to *tozti*.

Quick note on file structure
----------------------------

Most extensions do not serve directly their javascript files to *tozti*. They
often split their code in separate files, and use some build process to obtain
a single file ``build.js`` out of their code. This is the file that they send
to the client. We will not describe here how to setup such a build process, as
it would end up very much opinionated, and still would have to differ between
extensions. However it is very much recommended to proceed in such a way, and
the sample extensions available on our github page provide some insight as to
how things can be organised.

Going further with ``MANIFEST``
===============================

Here are a complete list of keys that ``MANIFEST`` can possess:

``router``
   This is used to declare new API endpoints. It should be an instance of
   :py:class:`tozti.utils.RouterDef`. More precisely it must have an
   :py:meth:`add_prefix` method and it will be passed to
   :py:meth:`aiohttp.web.UrlDispatcher.add_routes`. Every route declared will
   be prefixed by ``/api/<extension-name>``.

``includes``
   A list of css or js filenames that must be included in the main
   ``index.html``. Usually you will put there your ``main.js`` which contains
   the code to register or patch components.

``dependencies``
    A list of names of extensions that must be loaded before this extension in
    order for it to be working as intended.

For more advanced user, you can also add signals for the `aiohttp.web` in the
``MANIFEST``. Please see `aiohttp server documentation`_ to learn more about
signals.

``_god_mode``
   Beware, this can be dangerous if used incorrectly! This should be a function
   taking as argument the main :py:class:`aiohttp.web.Application` object.  You
   can use it to register custom middlewares or do otherwise weird stuff.

``on_response_prepare``
    This should be a function. It is a hook for changing HTTP headers for
    streamed responses and WebSockets.

``on_startup``
    This should be a function. Will be called during the startup of the
    application. Usefull to launch background services for exemple.

``on_cleanup``
    This should be a function. Will be called on application cleanup. You can
    use it to close connections to the database for exemple.

``on_shutdown``
    This should be a function. Will be closed on application shutdown.

Having a more complex server
============================

Sometimes you can find that putting the whole server part inside ``server.py`` is
a bit too restrictive. As your extension grow you'll probably want to refactor
it in several files. Tozti provide a way to do so. Instead of creating a
``server.py`` file, you could create a ``server/`` folder, and inside it write a
file ``__init__.py`` defining (at least) the ``MANIFEST`` structure.

.. _aiohttp server documentation: https://docs.aiohttp.org/en/stable/web.html
