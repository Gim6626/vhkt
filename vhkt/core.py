# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

try:
    import yaml
    import os.path
    import random
    from enum import Enum
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
    def key_combination_type_by_key(self, key):
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

    def key_combination_type_by_key(self, key):
        return self._data['actions'][key]['type']

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

    @abstractmethod
    def action_guesses(self, action_key) -> int:
        pass

    @abstractmethod
    def action_error_guesses(self, action_key) -> int:
        pass

    @abstractmethod
    def action_learning_in_process(self, action_key) -> bool:
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
    def actions_guesses_count(self) -> int:
        count = 0
        for key in self.actions_keys:
            if self.action_guesses(key) is not None:
                count += self.action_guesses(key)
        return count

    @property
    def actions_error_guesses_count(self) -> int:
        count = 0
        for key in self.actions_keys:
            if self.action_error_guesses(key) is not None:
                count += self.action_error_guesses(key)
        return count

    @property
    def actions_learning_in_process_count(self) -> int:
        count = 0
        for key in self.actions_keys:
            if self.action_learning_in_process(key):
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
                and self._data['actions'][action_key]['guesses'] > 0:
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
                if 'success' in self._data['actions'][action_key] \
                        and not self._data['actions'][action_key]['success'] \
                        or action_key not in self._data['actions'] \
                        or 'success' not in self._data['actions'][action_key]:
                    all_success = False
        return all_success

    @property
    def random_nonlearned_action_key(self):
        for _ in range(5):
            random_action_key_index = random.randint(0, len(self.actions_keys) - 1)
            random_action_key = self.actions_keys[random_action_key_index]
            if random_action_key in self.actions_keys \
                    and self.action_success(random_action_key):
                continue
            return random_action_key
        return None

    def save(self):
        with open(self.lrnres_file_path, 'w') as learning_results_file:
            learning_results_file_data = yaml.safe_dump(self._data)
            learning_results_file.write(learning_results_file_data)


class BasicTutor(ABC):

    class AnswerType(Enum):
        HELP = 'help'
        QUIT = 'quit'
        REGULAR_ANSWER = 'regular_answer'

    def __init__(self, hk_storage, learning_results_storage):
        self.hk_storage: BasicHotKeysStorage \
            = hk_storage
        self.learning_results_storage: BasicLearningResultsStorage \
            = learning_results_storage
        self.random_action_key = None

    def tutor(self):
        self.show_learning_stats()
        all_success = self.learning_results_storage.all_actions_learned_successfully
        if all_success:
            self.print('All hotkeys are learned, nothing to do')
            return
        while True:
            action_key, question = self.prepare_question()
            answer_type, answer = self.answer_for_question(question)
            if answer_type == self.AnswerType.HELP:
                self.show_help_for_action(action_key)
            elif answer_type == self.AnswerType.QUIT:
                return 0
            elif answer_type == self.AnswerType.REGULAR_ANSWER:
                if answer in self.hk_storage.action_hotkeys_by_key(action_key):
                    self.learning_results_storage.set_action_guess_correct(action_key)
                    self.print('Correct!')
                else:
                    self.learning_results_storage.set_action_guess_wrong(action_key)
                    self.print('Wrong!')
                    while True:
                        question = 'Want to see correct answer? [y/n]: '
                        answer_type, answer = self.answer_for_question(question)
                        if answer_type == self.AnswerType.REGULAR_ANSWER:
                            if answer == 'y':
                                self.show_help_for_action(action_key)
                                break
                            elif answer == 'n':
                                break
                            else:
                                self.print('You should type "y" or "n"')
                                continue
                        else:
                            raise ValueError(f'Invalid answer type {answer_type}')
            else:
                raise ValueError(f'Invalid answer type {answer_type}')
            self.show_learning_stats()
            self.after_answer()
            self.learning_results_storage.save()
            all_success = self.learning_results_storage.all_actions_learned_successfully
            if all_success:
                self.print('All hotkeys are learned, nothing more to do')
                return

    @abstractmethod
    def show_learning_stats(self):
        pass

    @abstractmethod
    def show_help_for_action(self, action_key):
        pass

    @abstractmethod
    def print(self, *args, **kwargs):
        pass

    def prepare_question(self):
        random_action_key = self.learning_results_storage.random_nonlearned_action_key
        if random_action_key is None:
            # TODO: Handle correctly
            raise Exception('random_action_key is None')
        key_combination_type = self.hk_storage.key_combination_type_by_key(random_action_key)
        if isinstance(key_combination_type, str):
            key_combination_type_str = key_combination_type
        elif isinstance(key_combination_type, list):
            key_combination_type_str = ' or '.join(key_combination_type)
        else:
            raise ValueError(f'Bad key combination type "{key_combination_type}", expected str or list')
        notes = self.notes_for_asked_action(random_action_key)
        question \
            = f'What is {key_combination_type_str} for "{self.hk_storage.action_description_by_key(random_action_key)}"?'.upper() \
              + f'\nType keys combination or "\\h" for help or "\\q" to quit'
        if len(notes) == 1:
            question += f'\nNOTE: {notes[0]}'
        elif len(notes) > 1:
            question += '\nNOTES:'
            for i, note in enumerate(notes):
                question += f'\n{i + 1}. {note}'
        return random_action_key, question

    @abstractmethod
    def answer_for_question(self, question):
        pass

    def notes_for_asked_action(self, action_key):
        notes = []
        key_combination_type = self.hk_storage.key_combination_type_by_key(action_key)
        if 'command' in key_combination_type:
            notes.append('Commands should be prepended with ":"')
        return notes

    def after_answer(self):
        pass


class ConsoleTutor(BasicTutor):

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def show_learning_stats(self):
        stats_lines = [
            f'{self.learning_results_storage.actions_learned_count} action(s) learned',
            f'{self.learning_results_storage.actions_learning_in_process_count} in process',
            f'{self.learning_results_storage.actions_guesses_count} guess(es)',
            f'{self.learning_results_storage.actions_error_guesses_count} error guess(es)',
            f'{self.learning_results_storage.actions_to_learn_count} left',
            f'{self.learning_results_storage.actions_count} total',
        ]
        self.print(', '.join(stats_lines))

    def show_help_for_action(self, action_key):
        hotkeys_str = '"' + '", "'.join(self.hk_storage.action_hotkeys_by_key(action_key)) + '"'
        self.print(f'Key combination(s) for "{self.hk_storage.action_description_by_key(action_key)}": {hotkeys_str}')

    def prepare_question(self):
        action_key, question = super().prepare_question()
        question += '\n> '
        return action_key, question

    def answer_for_question(self, question):
        answer = input(question)
        if answer == '\\h':
            answer_type = self.AnswerType.HELP
        elif answer == '\\q':
            answer_type = self.AnswerType.QUIT
        else:
            answer_type = self.AnswerType.REGULAR_ANSWER
        return answer_type, answer

    def notes_for_asked_action(self, action_key):
        notes = super().notes_for_asked_action(action_key)
        correct_answers = self.hk_storage.action_hotkeys_by_key(action_key)
        correct_answers_one_str = ';'.join(correct_answers)
        if '+' in correct_answers_one_str and '+' not in correct_answers:  # TODO: Make more correct check, what if "Ctrl++"?
            notes.append('If you need to use Ctrl or other special key in answer, type it\'s name plus regular key like "Ctrl+w"')
        if ',' in correct_answers_one_str and ',' not in correct_answers:  # TODO: Make more correct check, what if "Ctrl+,"?
            notes.append('If you need to type several keys combinations one by one, type them with comma separator like "Ctrl+x,Ctrl+x"')
        return notes

    def after_answer(self):
        self.print()
