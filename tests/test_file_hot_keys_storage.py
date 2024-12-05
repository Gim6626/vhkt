import pytest
import pathlib

import vhkt.filestorage


@pytest.fixture
def storage():
    stor = vhkt.filestorage.FileHotKeysStorage(pathlib.Path.cwd().parent / 'hkdb.yaml')
    return stor


def test_storage_not_empty(storage):
    assert storage.actions_keys
