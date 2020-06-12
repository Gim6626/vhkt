# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

from enum import Enum
from abc import ABC, abstractmethod, abstractproperty


class Mode(Enum):
    SIMPLE_TEXT = 'simple-text'
    CURSES_TEXT = 'curses-text'
    CURSES_TUI = 'curses-tui'


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

    @abstractmethod
    def remove_results_for_action(self, action_key):
        pass

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


class BasicTutor(ABC):

    class AnswerType(Enum):
        HELP = 'help'
        EXIT = 'exit'
        REGULAR_ANSWER = 'regular_answer'

    def __init__(self, hk_storage, learning_results_storage):
        self.hk_storage: BasicHotKeysStorage \
            = hk_storage
        self.learning_results_storage: BasicLearningResultsStorage \
            = learning_results_storage
        self.random_action_key = None

    def before_question(self):
        pass

    def before_success(self):
        pass

    def tutor(self):
        self.show_learning_stats()
        all_success = self.learning_results_storage.all_actions_learned_successfully
        success_str = 'All hotkeys are learned, nothing to do'
        if all_success:
            self.before_success()
            self.print(success_str)
            self.on_exit()
            return
        while True:
            self.before_question()
            action_key, question = self.prepare_question()
            answer_type, answer_blocks = self.answer_for_question(question)
            if answer_type == self.AnswerType.HELP:
                self.show_help_for_action(action_key)
            elif answer_type == self.AnswerType.EXIT:
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
                self.before_success()
                self.print(success_str)
                self.on_exit()
                return

    def show_help_for_action(self, action_key):
        helps = []
        for hotkey in self.hk_storage.action_hotkeys_by_key(action_key):
            if isinstance(hotkey, list):
                helps.append('"' + ','.join([f'{h}' for h in hotkey]) + '"')
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
        while True:
            random_action_key = self.learning_results_storage.random_nonlearned_action_key
            if random_action_key is None:
                raise Exception('random_action_key is None')
            try:
                key_combination_type = self.hk_storage.key_combination_type_by_key(random_action_key)
                break
            except KeyError as err:
                if random_action_key in str(err):
                    self.learning_results_storage.remove_results_for_action(random_action_key)
                else:
                    raise err
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
