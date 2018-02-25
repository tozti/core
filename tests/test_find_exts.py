import pytest
import os, sys, shutil

import tozti
import tozti.__main__
import tozti.app

from enum import Enum
import tests.commons as commons

class Ext_format(Enum):
    SERVER_FILE = 0
    SERVER_FOLDER = 1
    BAD_FORMAT = 2


@pytest.fixture(scope="function")
def empty_extensions_entry_leave(request):
    """
    Fixture that enable to clean `extensions/` folder before
    and after executing the test
    """
    commons.empty_extensions_list()
    request.addfinalizer(commons.empty_extensions_list)


@pytest.mark.parametrize("extensions",
        [
            [("foo", Ext_format.SERVER_FILE, {"name": "foo", "includes": ["a", "b"]})],
            [("foo", Ext_format.SERVER_FOLDER, {"name": "foo", "includes": ["a", "b"]})],
            [("bar", Ext_format.BAD_FORMAT, {})],
            [("foo", Ext_format.SERVER_FILE, None)],
            [("foo", Ext_format.SERVER_FILE, None), ("bar", Ext_format.SERVER_FILE, {"name": "bar"})],
            [("foo", Ext_format.SERVER_FILE, {"name": "foo"}), ("bar", Ext_format.SERVER_FILE, {"name": "bar"})],
        ]
        )
def test_find_exts(empty_extensions_entry_leave, extensions):
    """
    Test for find_exts function
    """
    # first, create the dummy extension
    # a dummy extension is parametrized as:
    #   - name, the name of the extension
    #   - add_single_file which is True if we want a server.py file, 
    #       otherwise a server/__init__.py file
    #   - manifest: the extension manifest. None if no manifest
    for name, ext_format, manifest in extensions:
        ext_path = os.path.join("extensions", name)
        os.mkdir(ext_path)
        file_path = "server.py"
        if ext_format == Ext_format.SERVER_FOLDER:
            file_path = "server/__init__.py"
            os.mkdir(os.path.join(ext_path, "server"))
        elif ext_format == Ext_format.BAD_FORMAT:
            file_path = "foo.py"
        file_path = os.path.join(ext_path, file_path)
        server_file = open(file_path, "w+")
        if manifest is not None:
            server_file.write("MANIFEST = {}".format(manifest))
        server_file.write("\n")
        server_file.close()

    # get the outputed result and the expected result
    output = list(tozti.__main__.find_exts())
    expected = [tozti.app.Extension(**manifest) \
            for name, ext_format, manifest in extensions   \
            if not (manifest is None or ext_format == Ext_format.BAD_FORMAT)]

    # special equality function, we want the result to be the
    # same for __dict__ equality
    assert(len(output) == len(expected))
    for ext in output:
        exist_corresponding = False
        for ext2 in expected:
            exist_corresponding |= (ext.__dict__ == ext2.__dict__)
        assert(exist_corresponding)

