import pytest
import pathlib

import vhkt.filestorage


@pytest.fixture
def storage():
    stor = vhkt.filestorage.FileHotKeysStorage(pathlib.Path(__file__).parent.parent / 'hotkeys' / 'vim.yaml')
    return stor


def test_storage_not_empty(storage):
    assert storage.actions_keys
