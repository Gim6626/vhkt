import yaml


class HotKeysDataBase:

    hkdb_file_path: str = None

    def __init__(self, hkdb_file_path: str):
        self.hkdb_file_path = hkdb_file_path
        with open(hkdb_file_path, 'r') as config_file:
            raw_data = config_file.read()
            self._data = yaml.safe_load(raw_data)

    @property
    def actions(self):
        return self._data['actions']
