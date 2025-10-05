# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com
import re

import yaml
import os
import random

from vhkt.basic import (
    BasicHotKeysStorage,
    BasicLearningResultsStorage,
)


class FileHotKeysStorage(BasicHotKeysStorage):

    hkdb_file_path: str = None

    def __init__(self, hkdb_file_path: str):
        self.hkdb_file_path = hkdb_file_path
        with open(hkdb_file_path, 'r') as config_file:
            raw_data = config_file.read()
            self._data = yaml.safe_load(raw_data)
            for action_key in self._data['actions'].keys():
                if 'type' not in self._data['actions'][action_key]:
                    self._data['actions'][action_key]['type'] = 'hotkey'

    @property
    def actions_keys(self):
        return list(self._data['actions'].keys())

    @property
    def app_name(self):
        return self._data['app']

    def action_description_by_key(self, key):
        return self._data['actions'][key]['description']

    def key_combination_type_by_key(self, key):
        return self._data['actions'][key]['type']

    def action_hotkeys_by_key(self, key):
        hotkeys_mod = []
        for hotkey in self._data['actions'][key]['hotkeys']:
            if isinstance(hotkey, list):
                hotkeys_mod.append(hotkey)
            elif isinstance(hotkey, str):
                if (len(hotkey) == 1
                        or ':' in hotkey
                        or 'Ctrl' in hotkey
                        or 'Shift' in hotkey
                        or 'Alt' in hotkey
                        or 'Space' in hotkey
                        or 'Home' in hotkey
                        or 'End' in hotkey
                        or 'Esc' in hotkey
                        or 'PgUp' in hotkey
                        or 'PgDn' in hotkey
                        or re.search(r'F\d+', hotkey)):
                    hotkeys_mod.append(hotkey)
                else:
                    hotkeys_mod.append(list(hotkey))
        return hotkeys_mod


class FileLearningResultsStorage(BasicLearningResultsStorage):

    lrnres_file_path: str = None

    def __init__(self, lrnres_file_path: str, hk_storage: BasicHotKeysStorage):
        self.lrnres_file_path = lrnres_file_path
        if os.path.isfile(self.lrnres_file_path):
            with open(lrnres_file_path, 'r') as fin:
                raw_data = fin.read()
                self._data = yaml.safe_load(raw_data)
        else:
            self._data = None
        if not self._data:
            self._data = {'actions': {}}
        for key in hk_storage.actions_keys:
            if key not in self.actions_keys:
                self._data['actions'][key] = {}
        self._prev_action_key = None
        self.hk_storage: BasicHotKeysStorage = hk_storage

    def remove_results_for_action(self, action_key):
        del self._data['actions'][action_key]

    @property
    def actions_keys(self):
        return list(self._data['actions'].keys())

    def action_success(self, action_key) -> bool:
        if 'success' in self._data['actions'][action_key] \
                and self._data['actions'][action_key]['success']:
            return True
        else:
            return False

    def action_guesses(self, action_key) -> int:
        if 'guesses' in self._data['actions'][action_key]:
            return self._data['actions'][action_key]['guesses']
        else:
            return None

    def action_error_guesses(self, action_key) -> int:
        if 'error_guesses' in self._data['actions'][action_key]:
            return self._data['actions'][action_key]['error_guesses']
        else:
            return None

    def action_learning_in_process(self, action_key) -> bool:
        if 'guesses' in self._data['actions'][action_key] \
                and self._data['actions'][action_key]['guesses'] > 0 \
                and ('success' not in self._data['actions'][action_key]
                     or not self._data['actions'][action_key]['success']):
            return True
        else:
            return False

    def set_action_learned_successfully(self, action_key):
        if action_key not in self._data['actions']:
            self._data['actions'][action_key] = {}
        self._data['actions'][action_key]['success'] = True

    def set_action_guess_correctness(self, action_key, correctness):
        if action_key not in self._data['actions']:
            self._data['actions'][action_key] = {}
        guesses_key = 'guesses'
        if guesses_key not in self._data['actions'][action_key]:
            self._data['actions'][action_key][guesses_key] = 1
        else:
            self._data['actions'][action_key][guesses_key] += 1
        correct_guesses_key = 'correct_guesses'
        if correct_guesses_key not in self._data['actions'][action_key]:
            if correctness:
                self._data['actions'][action_key][correct_guesses_key] = 1
            else:
                self._data['actions'][action_key][correct_guesses_key] = 0
        else:
            if correctness:
                self._data['actions'][action_key][correct_guesses_key] += 1
                if self._data['actions'][action_key][correct_guesses_key] >= self.CORRECT_ANSWERS_TO_LEARN:
                    self.set_action_learned_successfully(action_key)
            else:
                if self._data['actions'][action_key][correct_guesses_key] > 0:
                    self._data['actions'][action_key][correct_guesses_key] -= 1
        error_guesses_key = 'error_guesses'
        if error_guesses_key not in self._data['actions'][action_key]:
            if not correctness:
                self._data['actions'][action_key][error_guesses_key] = 1
            else:
                self._data['actions'][action_key][error_guesses_key] = 0
        else:
            if not correctness:
                self._data['actions'][action_key][error_guesses_key] += 1

    @property
    def all_actions_learned_successfully(self) -> bool:
        all_success = True
        if self._data['actions'] == {}:
            all_success = False
        else:
            for action_key, action_value in self._data['actions'].items():
                if action_key not in self.hk_storage.actions_keys:
                    continue
                if 'success' in self._data['actions'][action_key] \
                        and not self._data['actions'][action_key]['success'] \
                        or action_key not in self._data['actions'] \
                        or 'success' not in self._data['actions'][action_key]:
                    all_success = False
        return all_success

    @property
    def random_nonlearned_action_key(self):
        repeats = 0
        repeats_limit = 5
        while True:
            if self.all_actions_learned_successfully:
                return None
            random_action_key_index = random.randint(0, len(self.actions_keys) - 1)
            random_action_key = self.actions_keys[random_action_key_index]
            if random_action_key in self.actions_keys \
                    and self.action_success(random_action_key):
                continue
            if random_action_key == self._prev_action_key \
                    and repeats < repeats_limit:
                repeats += 1
                continue
            self._prev_action_key = random_action_key
            return random_action_key
        return None

    def save(self):
        with open(self.lrnres_file_path, 'w') as learning_results_file:
            learning_results_file_data = yaml.safe_dump(self._data)
            learning_results_file.write(learning_results_file_data)
