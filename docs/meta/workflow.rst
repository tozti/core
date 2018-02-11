*************************************
Workflow for developping an extension
*************************************

This is a short guide on how to develop extensions efficiently.

Creating a new extension
========================

To create an extension, download the files contained inside the repository 
`tozti-boilerplate`_.This will setup the build process in order to develop 
an extension using ``sass`` and ``vue-js``.

Working on an extension
=======================

Working on an extension can be splitted into several steps:

Firstly, you must install the extension. For that, first install Tozti and
then either:

- clone the extension you want to work on inside ``tozti/extensions``
- clone the extension elsewhere and create a simlink from 
  ``tozti/extensions/<yourextensionname>`` to the directory of the extension 
  (for more 'advanced' users)


Secondly, setup your extension. For instance, execute ``npm install`` and 
``npm run build`` (inside your extension's directory).

Then, launch Tozti in the background. If, while you're developping your 
extension, you are updating the server part of the extension, then you 
will have to stop and start Tozti again. Otherwise if you are only working 
on the javascript part you should not touch to Tozti anymore.

Finally, you can execute ``npm run watch`` in the background. This will
allow the javascript part of the extension to be build automatically. You 
should not touch to this process either. 

If you followed every step, then to see the changes you made to your extension 
you should only have to reload the webpage inside your webbrowser!




.. _tozti-boilerplate: https://github.com/tozti/tozti-boilerplate

