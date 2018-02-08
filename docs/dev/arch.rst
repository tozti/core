************
Architecture
************


Tozti serves 3 main HTTP namespaces:

- ``/static``: usual static files (javascript, css, images, etc)
- ``/api``: REST endpoints to interact with the server
- anything else will be responded to with the main ``index.html``


Extensions
==========

The tozti core is really lightweight but it has the ability to load extensions.
During the startup, the server will search for extensions in the ``extensions``
subfolder of the tozti repository root.

Directory structure and ``server.py``
-------------------------------------

An extension is a folder (whose name will determine the prefix under which the
extension's files are served) containing at least a ``server.py`` file (or
``server/__init__.py``). This file must contain a global variable ``MANIFEST``
that is a dictionary containing the following keys (any one being optional):

The tozti core is really lightweight but it has the ability to load extensions.
For now, you only need to know that extension is a folder providing a python
file (`server.py`), describing how the extension works on the server (its
routes, which files must be included from the client...).
An extension can be installed by pasting its folder inside tozti's
`extensions/` folder. During startup, the server will go through every
subfolders of `extensions/` and try to load them as an extension.

``includes``
   A list of css or js files that must be included in the main ``index.html``.
   Usually you will put there ``"main.js"`` which contains the code to register
   or patch components. The file paths must be relative to the ``dist``
   subfolder of the extension (see below).

``_god_mode``
   Beware, this can be dangerous if used incorrectly! This should be a function
   taking as argument the main :py:class:`aiohttp.web.Application` object.  You
   can use it to register custom middlewares or do otherwise weird stuff.

The extension can contain a ``dist`` folder. The content of this folder will
be served at the URL ``/static/<extension-name>``.

Vuejs initialization
--------------------

* See example in branch `sample-extension
  <https://github.com/tozti/tozti/tree/sample-extension/extensions/hello-world>`_.
* See an `intro <https://vuejs.org/v2/guide/#Composing-with-Components>`_
  and some `doc <https://vuejs.org/v2/guide/components.html>`_ on components.
* See `template syntax <https://vuejs.org/v2/guide/syntax.html>`_.
