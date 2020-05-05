# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

try:
    import yaml
    import os.path
    import random
    from abc import ABC, abstractmethod, abstractproperty
except ModuleNotFoundError as e:
    import sys
    import os.path
    from inspect import getsourcefile
    current_dir = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))
    parent_dir = os.path.realpath(os.path.join(current_dir, '..'))
    frmt_str = 'Try to install requirements using command '\
               + '\'pip3 install -r requirements.txt\' from "{}" '\
               + 'directory or from virtual env (better)'
    print('ERROR: ' + str(e) + '. ' + frmt_str.format(parent_dir))
    sys.exit(1)


class BasicHotKeysStorage(ABC):

    @property
    @abstractmethod
    def actions_keys(self):
        pass

    @abstractmethod
    def action_description_by_key(self, key):
        pass

    @abstractmethod
    def action_hotkeys_by_key(self, key):
        pass


class FileHotKeysStorage(BasicHotKeysStorage):

    hkdb_file_path: str = None

    def __init__(self, hkdb_file_path: str):
        self.hkdb_file_path = hkdb_file_path
        with open(hkdb_file_path, 'r') as config_file:
            raw_data = config_file.read()
            self._data = yaml.safe_load(raw_data)

    @property
    def actions_keys(self):
        return list(self._data['actions'].keys())

    def action_description_by_key(self, key):
        return self._data['actions'][key]['description']

    def action_hotkeys_by_key(self, key):
        return self._data['actions'][key]['hotkeys']


class BasicLearningResultsStorage(ABC):

    CORRECT_ANSWERS_TO_LEARN = 3

    @property
    @abstractmethod
    def actions_keys(self):
        pass

    @abstractmethod
    def action_success(self, action_key) -> bool:
        pass

    @property
    def actions_count(self) -> int:
        return len(self.actions_keys)

    @property
    def actions_learned_count(self) -> int:
        count = 0
        for key in self.actions_keys:
            if self.action_success(key):
                count += 1
        return count

    @property
    def actions_to_learn_count(self) -> int:
        return self.actions_count - self.actions_learned_count

    @abstractmethod
    def set_action_learned_successfully(self, action_key):
        pass

    @property
    @abstractmethod
    def all_actions_learned_successfully(self) -> bool:
        pass

    @abstractmethod
    def set_action_guess_correctness(self, action_key, correctness):
        pass

    def set_action_guess_correct(self, action_key):
        self.set_action_guess_correctness(action_key, True)

    def set_action_guess_wrong(self, action_key):
        self.set_action_guess_correctness(action_key, False)

    @property
    @abstractmethod
    def random_nonlearned_action_key(self):
        pass

    def save(self):
        pass


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

    @property
    def actions_keys(self):
        return list(self._data['actions'].keys())

    def action_success(self, action_key) -> bool:
        if 'success' in self._data['actions'][action_key] \
                and self._data['actions'][action_key]['success']:
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
                if self._data['actions'][action_key][correct_guesses_key] == self.CORRECT_ANSWERS_TO_LEARN:
                    self.set_action_learned_successfully(action_key)
            else:
                if self._data['actions'][action_key][correct_guesses_key] > 0:
                    self._data['actions'][action_key][correct_guesses_key] -= 1

    @property
    def all_actions_learned_successfully(self) -> bool:
        all_success = True
        if self._data['actions'] == {}:
            all_success = False
        else:
            for action_key, action_value in self._data['actions'].items():
                if 'success' in self._data['actions'][action_key] \
                        and not self._data['actions'][action_key]['success'] \
                        or action_key not in self._data['actions'] \
                        or 'success' not in self._data['actions'][action_key]:
                    all_success = False
        return all_success

    @property
    def random_nonlearned_action_key(self):
        random_action_key_index = random.randint(0, len(self.actions_keys) - 1)
        random_action_key = self.actions_keys[random_action_key_index]
        if random_action_key in self.actions_keys \
                and self.action_success(random_action_key):
            return None
        return random_action_key

    def save(self):
        with open(self.lrnres_file_path, 'w') as learning_results_file:
            learning_results_file_data = yaml.safe_dump(self._data)
            learning_results_file.write(learning_results_file_data)
