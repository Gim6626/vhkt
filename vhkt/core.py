# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

try:
    import yaml
    import os.path
    import random
    import string
    import curses
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
        hotkeys_mod = []
        for hotkey in self._data['actions'][key]['hotkeys']:
            if isinstance(hotkey, list):
                hotkeys_mod.append(hotkey)
            elif isinstance(hotkey, str):
                if len(hotkey) == 1:
                    hotkeys_mod.append(hotkey)
                elif ':' in hotkey:
                    hotkeys_mod.append(hotkey)
                else:
                    hotkeys_mod.append(list(hotkey))
        return hotkeys_mod


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

    def before_question(self):
        pass

    def tutor(self):
        self.show_learning_stats()
        all_success = self.learning_results_storage.all_actions_learned_successfully
        success_str = 'All hotkeys are learned, nothing to do'
        if all_success:
            self.print(success_str)
            self.on_exit()
            return
        while True:
            self.before_question()
            action_key, question = self.prepare_question()
            answer_type, answer_blocks = self.answer_for_question(question)
            if answer_type == self.AnswerType.HELP:
                self.show_help_for_action(action_key)
            elif answer_type == self.AnswerType.QUIT:
                return 0
            elif answer_type == self.AnswerType.REGULAR_ANSWER:
                if len(answer_blocks) > 1 and answer_blocks in self.hk_storage.action_hotkeys_by_key(action_key) \
                        or len(answer_blocks) == 1 and answer_blocks[0] in self.hk_storage.action_hotkeys_by_key(action_key):
                    self.learning_results_storage.set_action_guess_correct(action_key)
                    self.print('Correct!')
                else:
                    self.learning_results_storage.set_action_guess_wrong(action_key)
                    self.print('Wrong!')
                    while True:
                        question = 'Want to see correct answer? [y/n]: '
                        answer_type, answer_blocks = self.answer_for_question(question)
                        if answer_type == self.AnswerType.REGULAR_ANSWER:
                            if answer_blocks == ['y']:
                                self.show_help_for_action(action_key)
                                break
                            elif answer_blocks == ['n']:
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
                self.print(success_str)
                self.on_exit()
                return

    def show_help_for_action(self, action_key):
        helps = []
        for hotkey in self.hk_storage.action_hotkeys_by_key(action_key):
            if isinstance(hotkey, list):
                helps.append(','.join([f'{h}' for h in hotkey]))
            elif isinstance(hotkey, str):
                helps.append(f'"{hotkey}"')
            else:
                raise NotImplementedError
        hotkeys_str = ' or '.join(helps)
        self.print(f'\nKey combination(s) for "{self.hk_storage.action_description_by_key(action_key)}": {hotkeys_str}')

    @abstractmethod
    def print(self, msg):
        pass

    def on_exit(self):
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
            = f'What is {key_combination_type_str} for "{self.hk_storage.action_description_by_key(random_action_key)}"?'.upper()
        if len(notes) == 1:
            question += f'\nNOTE: {notes[0]}'
        elif len(notes) > 1:
            question += '\nNOTES:'
            for i, note in enumerate(notes):
                question += f'\n{i + 1}. {note}'
        question += '\n> '
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

    def show_learning_stats(self):
        stats_lines = [
            f'{self.learning_results_storage.actions_learned_count} action(s) learned',
            f'{self.learning_results_storage.actions_learning_in_process_count} in process',
            f'{self.learning_results_storage.actions_guesses_count} guess(es)',
            f'{self.learning_results_storage.actions_error_guesses_count} error guess(es)',
            f'{self.learning_results_storage.actions_to_learn_count} action(s) left to learn',
            f'{self.learning_results_storage.actions_count} action(s) total to learn',
        ]
        self.print(', '.join(stats_lines))


class ConsoleTutor(BasicTutor):

    def print(self, msg):
        print(msg)

    def show_help_for_action(self, action_key):
        super().show_help_for_action(action_key)
        input('Press any key to continue')

    def answer_for_question(self, question):
        answer = input(question)
        if answer == '\\h':
            answer_type = self.AnswerType.HELP
        elif answer == '\\q':
            answer_type = self.AnswerType.QUIT
        else:
            answer_type = self.AnswerType.REGULAR_ANSWER
        return answer_type, answer.split(',')

    def notes_for_asked_action(self, action_key):
        notes = super().notes_for_asked_action(action_key)
        correct_answers = self.hk_storage.action_hotkeys_by_key(action_key)
        list_found = False
        ctrl_found = False
        several_keys_note = 'If you need to type several keys combinations one by one, type them with comma separator like "a,b"'
        ctrl_note = 'If you need to use Ctrl or other special key in answer, type it\'s name plus regular key like "Ctrl+w"'
        for correct_answer in correct_answers:
            if isinstance(correct_answer, list):
                if not list_found:
                    notes.append(several_keys_note)
                    list_found = True
                elif 'Ctrl' in correct_answer and not ctrl_found:
                    notes.append(ctrl_note)
                    ctrl_found = True
            elif isinstance(correct_answer, str):
                if 'Ctrl' in correct_answer and not ctrl_found:
                    notes.append(ctrl_note)
                    ctrl_found = True
        notes.append('Type keys combination or "\\h" for help or "\\q" to quit')
        return notes

    def after_answer(self):
        self.print('')


class CursesTutor(BasicTutor):

    def __init__(self, hk_storage, learning_results_storage, window):
        super().__init__(hk_storage, learning_results_storage)
        self.window = window

    def show_help_for_action(self, action_key):
        super().show_help_for_action(action_key)
        self.print('Press any key to continue', newline=False)
        self.window.getkey()

    def on_exit(self):
        self.print('Press any key to exit', newline=False)
        self.window.getkey()

    def print(self, msg, newline=True):
        if newline:
            msg += '\n'
        self.window.addstr(msg)

    def notes_for_asked_action(self, action_key):
        notes = super().notes_for_asked_action(action_key)
        notes.append('Type keys combination or "Ctrl+h" for help or "Ctrl+e" to quit')
        return notes

    def answer_for_question(self, question):
        self.print(question, newline=False)
        answer_blocks = []
        last_combo = False
        while True:
            key = self.window.getkey()
            if key in string.ascii_lowercase or key in string.ascii_uppercase:
                key_modified = key
            elif len(key) == 1 and 1 <= ord(key) <= 32:
                key_modified = f'Ctrl+{string.ascii_lowercase[ord(key) - 1]}'
                last_combo = True
            else:
                key_modified = key
            if key_modified != 'Ctrl+j':
                if last_combo and len(answer_blocks) > 0:
                    self.print(',', newline=False)
                    last_combo = False
                self.print(key_modified, newline=False)
            else:
                self.print(key, newline=False)
            answer_blocks.append(key_modified)
            if key == os.linesep \
                    or key_modified == 'Ctrl+h' \
                    or key_modified == 'Ctrl+e':
                break
        if answer_blocks == ['Ctrl+h']:
            answer_type = self.AnswerType.HELP
        elif answer_blocks == ['Ctrl+e']:
            answer_type = self.AnswerType.QUIT
        else:
            answer_type = self.AnswerType.REGULAR_ANSWER
        answer_blocks = answer_blocks[:-1]
        if len(answer_blocks) > 1 and answer_blocks[0] == ':':
            s = ''
            for c in answer_blocks:
                s += c
            answer_blocks = [s]
        return answer_type, answer_blocks

    def before_question(self):
        self.window.clear()

    def after_answer(self):
        self.print('')
