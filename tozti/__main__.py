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

# You should have received a copy of the GNU Affero General Public Licensefoo/blo/baz
# along with Tozti.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import asyncio
from importlib.util import spec_from_file_location, module_from_spec
import os
import sys

import logbook
import toml

import tozti
import tozti.store
import tozti.app
import tozti.auth
from tozti.utils import ConfigError

logger = logbook.Logger('tozti.main')


def find_exts():
    """Register the extensions found.

    Returns the list of includes and the list of static directories. See
    the `docs`_ for the manifest format.

    .. docs: https://tozti.readthedocs.io/en/latest/dev/arch.html#extensions
    """
    for extname in os.listdir(os.path.join(tozti.TOZTI_BASE, 'extensions')):
        extpath = os.path.join(tozti.TOZTI_BASE, 'extensions', extname)
        if not os.path.isdir(extpath):
            continue

        logger.info('Loading extension {}'.format(extname))

        mod_path = os.path.join(extpath, 'server.py')
        pkg_path = os.path.join(extpath, 'server', '__init__.py')

        if os.path.isfile(mod_path):
            spec = spec_from_file_location(extname, mod_path)
        elif os.path.isfile(pkg_path):
            spec = spec_from_file_location(extname, pkg_path)
        else:
            msg = 'Could not find python file for extension {}'
            # could not use logger.exception as we do not have any exceptions
            # instead we use logger.error
            logger.error(msg.format(extname))
            continue

        mod = module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as err:
            msg = 'Error while loading extension {}, skipping: {}'
            logger.exception(msg.format(extname, err))
            continue

        try:
            #FIXME: validate the manifest format
            # the manifest format is more or less validated inside of the constructor, 
            # but I agree, it has to be done

            if 'name' not in mod.MANIFEST:
                logger.error('Error while loading extension {}, MANIFEST'
                             'does not contain the `name`'
                             'property'.format(extname))

            yield tozti.app.Extension(**mod.MANIFEST)
        except AttributeError:
            logger.exception('Error while loading extension {}, skipping: no '
                             'MANIFEST found'.format(extname))
            continue


def load_config_file(path = "config.toml"):
    """Load tozti's configuration file.
    TODO: add validation

    Args:
        path (str): the path where the config file should be

    Returns:
        a dictionnary representing the config file

    Raises:
        Exception if the file couldn't be loaded
    """

    # put this in a function for the moment when validation will be done
    config = {}
    required = {"http":["host", "port"], 
                "mongodb":["host", "port"], 
                "cookie": ["private_key", "public_key"]}
    with open(path) as s:
        config = toml.load(s)

    for major in required:
        if not major in config:
            raise ConfigError("Expected a {} entry".format(major))
        else:
            for minor in required[major]:
                if not minor in config[major]:
                    raise ConfigError("Entry {} expected sub-entry {}".format(major, minor))
    return config




def main():
    """Entry point for server startup."""

    # Fix for some Python implementations that do not create a default event loop (?!)
    asyncio.set_event_loop(asyncio.new_event_loop())

    parser = argparse.ArgumentParser('tozti')
    parser.add_argument(
        '-c', '--config', default=os.path.join(tozti.TOZTI_BASE, 'config.toml'),
        help='configuration file (default: `TOZTI/config.toml`)')
    parser.add_argument('command', choices=('dev', 'prod'))
    args = parser.parse_args()

    tozti.PRODUCTION = args.command == 'prod'

    # logging handlers
    # FIXME: make things fancier and configurable (logrotate, etc)
    logbook.compat.redirect_logging()
    if args.command == 'dev':
        handler = logbook.StreamHandler(sys.stdout)
        handler.push_application()

    # config file
    logger.debug('Loading configuration'.format(args.config))
    try:
        config = load_config_file(args.config)
    except Exception as err:
        logger.critical('Error while loading configuration: {}'.format(err))
        sys.exit(1)
    tozti.CONFIG = config

    # initialize app
    logger.debug('Initializing app')
    app = tozti.app.App()

    # load and register extensions
    # ISSUE
    # Now every extension is forced to have a dist folder 
    try:
        for extension in find_exts():
            # add dependency on the core
            extension.dependencies.add('core')
            # static dir is only important if some files are included by the extension
            if len(extension.includes) > 0:
                # make static_dir absolute and default to 'dist' if some files are included
                if extension.static_dir is None :
                    extension.static_dir = 'dist'
                extension.set_static_dir_absolute(
                    os.path.join(tozti.TOZTI_BASE, 'extensions', extension.name))
            app.register(extension)
    except Exception as err:
        logger.critical('Error while loading extensions: {}'
                        .format(err), exc_info=sys.exc_info())
        sys.exit(1)

    try:
        app.main()
    except tozti.app.DependencyCycle as err:
        logger.critical('Found dependency cycle between extensions {} and {}'
                        .format(err.args[0], err.args[1]))
    except Exception as err:
        logger.critical('Fatal server error: {}'.format(err),
                        exc_info=sys.exc_info())
        sys.exit(1)


if __name__ == "__main__":
    main()
