# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

import curses
import random
from typing import List, Sequence
from enum import Enum
import string

import vhkt.basic
from vhkt.basic import BasicTutor


class ColorMode(Enum):
    REGULAR = 1
    STATUS_BAR = 2
    STATISTICS = 3
    QUESTION = 4
    SUCCESS = 5
    ERROR = 6


class InterfaceState(Enum):
    ASKING_QUESTION = 'asking-question'
    ANSWER_INPUT = 'answer-input'
    CHECKING_ANSWER = 'check-answer'
    CORRECT_ANSWER = 'correct-answer'
    INCORRECT_ANSWER = 'incorrect-answer'
    CHECKING_IF_HELP_IS_NEEDED = 'checking-if-help-is-needed'
    SHOWING_HELP = 'showing-help'
    ALL_SUCCESS = 'all-success'
    PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP = 'pending-enter'
    SKIP_ACTION = 'skip-action'
    QUIT = 'quit'


class DisplayBlock:

    def __init__(self,
                 color_mode: ColorMode,
                 text: str):
        self.color_mode: ColorMode = color_mode
        self._text: str = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value


class EmptyDisplayBlock(DisplayBlock):

    def __init__(self):
        super().__init__(ColorMode.REGULAR, '')


class InputAnswerDisplayBlock(DisplayBlock):

    PROMPT = '> '

    def __init__(self):
        super().__init__(ColorMode.REGULAR, self.PROMPT)
        self.input_key_combinations = []

    @property
    def text(self):
        text = self.PROMPT
        if len(self.input_key_combinations) > 0 \
                and self.input_key_combinations[0] == ':':
            text += ''.join(self.input_key_combinations)
        else:
            text += ', '.join(self.input_key_combinations)
        return text

    @text.setter
    def text(self, value):
        raise NotImplementedError


class AnswerOptionsDisplayBlock(DisplayBlock):

    def __init__(self, correct_answer, options: Sequence[str]):
        lines = []
        for i, option in enumerate(options):
            option_str = " or ".join(option) if isinstance(option, list) else option
            line = f'{i + 1}. {str(option_str)}'
            lines.append(line)
        text = '\n'.join(lines)
        self.correct_answer = correct_answer
        self.options = options
        super().__init__(ColorMode.REGULAR, text)


class CursesTuiTutor(BasicTutor):

    COLOR_MODE_MAP = {
        ColorMode.REGULAR: (
            curses.COLOR_WHITE,
            curses.COLOR_BLACK,
        ),
        ColorMode.STATUS_BAR: (
            curses.COLOR_BLACK,
            curses.COLOR_WHITE,
        ),
        ColorMode.STATISTICS: (
            curses.COLOR_CYAN,
            curses.COLOR_BLACK,
        ),
        ColorMode.QUESTION: (
            curses.COLOR_BLUE,
            curses.COLOR_BLACK,
        ),
        ColorMode.SUCCESS: (
            curses.COLOR_GREEN,
            curses.COLOR_BLACK,
        ),
        ColorMode.ERROR: (
            curses.COLOR_MAGENTA,
            curses.COLOR_BLACK,
        )
    }

    OBSOLETE_ANSWER_MODE_WARNING = f'WARNING: "{vhkt.basic.AnswerMode.INPUT.value}" answer mode is deprecated, may not work properly and possibly will be removed in future versions. Please use "{vhkt.basic.AnswerMode.SELECT.value}" answer mode instead.'

    def __init__(self, hk_storage, learning_results_storage, answer_mode, window):
        super().__init__(hk_storage, learning_results_storage)
        self.window = window
        self._input_string = ''
        self._display_blocks: List[DisplayBlock] = []
        self._interface_state: InterfaceState = InterfaceState.ASKING_QUESTION
        self._debug_msg = None
        self._action_key = None
        self._next_interface_state: InterfaceState = None  # Used only to choose next step for PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP
        self._answer_mode = answer_mode

    def show_welcome_message(self):
        self._display_blocks = (
            DisplayBlock(ColorMode.REGULAR, self.WELCOME_STRING),
            DisplayBlock(ColorMode.REGULAR, self.selected_application_string),
            DisplayBlock(ColorMode.REGULAR, 'Press any key to continue'),
        )
        self._render_display_blocks()
        self.window.getch()

    def show_obsolete_interface_mode_warning(self):
        pass

    def show_obsolete_answer_mode_warning(self):
        self._display_blocks = (
            DisplayBlock(ColorMode.REGULAR, self.OBSOLETE_ANSWER_MODE_WARNING),
            DisplayBlock(ColorMode.REGULAR, 'Press any key to continue'),
        )
        self._render_display_blocks()
        self.window.getch()

    @property
    def _statusbar_str(self):
        s = f'Press "Ctrl+e" to exit, "Ctrl+h" for help about hotkey for current action or "Ctrl+k" to skip this action and do not ask hotkeys for it'
        # TODO: Align debug message right
        if self._debug_msg is not None:
            s += ' | ' + self._debug_msg
        return s

    def print(self, msg):
        raise NotImplementedError

    def answer_for_question(self, question):
        raise NotImplementedError

    @property
    def _center_text_pos_y(self):
        return int((self._height // 2) - 2)

    @property
    def _height(self):
        return self.window.getmaxyx()[0]

    @property
    def _width(self):
        return self.window.getmaxyx()[1]

    def _prepare(self):
        # Clear and refresh the screen for a blank canvas
        self.window.clear()
        self.window.refresh()

        # Disable cursor
        curses.curs_set(0)

        # Start colors in curses
        curses.start_color()
        for color_mode, (fg_color, bg_color) in self.COLOR_MODE_MAP.items():
            curses.init_pair(color_mode.value, fg_color,  bg_color)

    def _render_statistics(self):
        statistics_str = ', '.join(self.learning_stats)
        self.window.addstr(0, 0, statistics_str, curses.color_pair(ColorMode.STATISTICS.value))

    def _render_statusbar(self):
        self.window.attron(curses.color_pair(ColorMode.STATUS_BAR.value))
        self.window.addstr(self._height - 1, 0, self._statusbar_str)
        self.window.addstr(self._height - 1, len(self._statusbar_str), " " * (self._width - len(self._statusbar_str) - 1))
        self.window.attroff(curses.color_pair(ColorMode.STATUS_BAR.value))

    def tutor(self):
        try:
            self._tutor_internal()
        except Exception as e:
            if str(e) == 'addwstr() returned ERR':
                raise Exception('Curses error, possible too small screen. If not - sorry and contact developers please.')
            else:
                raise e

    def _tutor_internal(self):
        # TODO: Think about implementing more universal basic tutor
        self._prepare()
        k = 0
        self.show_welcome_message()
        if self._answer_mode == vhkt.basic.AnswerMode.INPUT:
            self.window.clear()
            self.show_obsolete_answer_mode_warning()
        while True:
            self.window.clear()
            self._render_statistics()
            self._render_statusbar()

            if k == 5:
                # "Ctrl+e" pressed
                break

            all_success = self.learning_results_storage.all_actions_learned_successfully
            if all_success \
                    and self._interface_state != InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP\
                    and self._interface_state != InterfaceState.QUIT:
                self._interface_state = InterfaceState.ALL_SUCCESS

            if self._interface_state == InterfaceState.ALL_SUCCESS:
                self._display_blocks = [
                    DisplayBlock(ColorMode.SUCCESS,
                                 self.success_string),
                    DisplayBlock(ColorMode.REGULAR,
                                 'Press ENTER to continue'),
                ]
                self._interface_state = InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP
                self._next_interface_state = InterfaceState.QUIT
            elif self._interface_state == InterfaceState.ASKING_QUESTION:
                self._action_key, question, notes = self.prepare_question()
                if self._answer_mode == vhkt.basic.AnswerMode.SELECT:
                    tip_text = 'Press correct hotkey index'
                else:
                    tip_text = 'Input hotkey or command and press ENTER'
                self._display_blocks = [
                    DisplayBlock(ColorMode.QUESTION,
                                 question),
                    DisplayBlock(ColorMode.REGULAR,
                                 tip_text),
                ]
                notes_mod = []
                if len(notes) == 1:
                    notes_mod.append(f'NOTE: {notes[0]}')
                elif len(notes) > 1:
                    notes_mod.append('NOTES:')
                    for i, note in enumerate(notes):
                        question += f'\n{i + 1}. {note}'
                if notes_mod:
                    self._display_blocks += [DisplayBlock(ColorMode.REGULAR,
                                                          note)
                                             for note in notes_mod]
                self._display_blocks += [EmptyDisplayBlock()]
                if self._answer_mode == vhkt.basic.AnswerMode.SELECT:
                    correct_answer = self.hk_storage.action_hotkeys_by_key(self._action_key)
                    other_random_keys_count = min(len(self.hk_storage.actions_keys) - 1, 3)
                    actions_keys_without_correct_one = [action_key for action_key in self.hk_storage.actions_keys if action_key != self._action_key]
                    other_random_keys = random.sample(actions_keys_without_correct_one, other_random_keys_count)
                    other_answers = [self.hk_storage.action_hotkeys_by_key(action_key) for action_key in other_random_keys]
                    answers = [correct_answer] + other_answers
                    random.shuffle(answers)
                    answer_options_display_block = AnswerOptionsDisplayBlock(correct_answer, answers)
                    self._display_blocks += [answer_options_display_block]
                    self._display_blocks += [EmptyDisplayBlock()]
                self._display_blocks += [InputAnswerDisplayBlock()]
                self._interface_state = InterfaceState.ANSWER_INPUT
            elif self._interface_state == InterfaceState.ANSWER_INPUT:
                if isinstance(self._display_blocks[-3], AnswerOptionsDisplayBlock):
                    answer_options_display_block: AnswerOptionsDisplayBlock = self._display_blocks[-3]
                    input_answer_display_block: InputAnswerDisplayBlock = self._display_blocks[-1]
                    key = chr(k)
                    if k == 8:
                        # "Ctrl+h" pressed
                        self._interface_state = InterfaceState.SHOWING_HELP
                        continue
                    if k == 11:
                        # "Ctrl+k" pressed
                        self._interface_state = InterfaceState.SKIP_ACTION
                        continue
                    if key in string.digits and 0 < int(key) <= len(answer_options_display_block.options):
                        self._input_string = key
                        input_answer_display_block.input_key_combinations.append(key)
                        self._interface_state = InterfaceState.CHECKING_ANSWER
                elif isinstance(self._display_blocks[-1], InputAnswerDisplayBlock):
                    input_answer_display_block: InputAnswerDisplayBlock = self._display_blocks[-1]
                    key = chr(k)
                    if k == 263:
                        # KEY_BACKSPACE
                        if len(input_answer_display_block.input_key_combinations) > 0:
                            del input_answer_display_block.input_key_combinations[-1]
                        key_modified = None
                    elif k == 8:
                        # "Ctrl+h" pressed
                        self._interface_state = InterfaceState.SHOWING_HELP
                        continue
                    elif k == 10:
                        # ENTER, Ctrl+j
                        key_modified = None
                        self._interface_state = InterfaceState.CHECKING_ANSWER
                        continue
                    elif k == 11:
                        # "Ctrl+k" pressed
                        self._interface_state = InterfaceState.SKIP_ACTION
                        continue
                    elif key in string.ascii_lowercase \
                            or key in string.ascii_uppercase \
                            or key in string.punctuation \
                            or key in string.digits:
                        key_modified = key
                    elif 1 <= k <= 32:
                        key_modified = f'Ctrl+{string.ascii_lowercase[ord(key) - 1]}'
                    else:
                        key_modified = None
                    if key_modified is not None:
                        input_answer_display_block.input_key_combinations.append(key_modified)
                else:
                    ValueError(f'Invalid last display block type "{type(self._display_blocks[-1])}"')
            elif self._interface_state == InterfaceState.SKIP_ACTION:
                self._display_blocks = [
                    DisplayBlock(ColorMode.ERROR,
                                 f'Action "{self.hk_storage.action_description_by_key(self._action_key)}" skipped'),
                    DisplayBlock(ColorMode.REGULAR,
                                 'Press ENTER to continue')
                ]
                self.learning_results_storage.skip_action(self._action_key)
                self.learning_results_storage.save()
                self._interface_state = InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP
                self._next_interface_state = InterfaceState.ASKING_QUESTION
            elif self._interface_state == InterfaceState.CHECKING_ANSWER:
                if isinstance(self._display_blocks[-3], AnswerOptionsDisplayBlock):
                    input_answer_display_block: InputAnswerDisplayBlock = self._display_blocks[-1]
                    if k == 263:
                        # KEY_BACKSPACE
                        if len(input_answer_display_block.input_key_combinations) > 0:
                            del input_answer_display_block.input_key_combinations[-1]
                            self._interface_state = InterfaceState.ANSWER_INPUT
                            continue
                    answer_options_display_block: AnswerOptionsDisplayBlock = self._display_blocks[-3]
                    input_answer = int(self._input_string) - 1
                    if answer_options_display_block.options[input_answer] == answer_options_display_block.correct_answer:
                        self._interface_state = InterfaceState.CORRECT_ANSWER
                    else:
                        self._interface_state = InterfaceState.INCORRECT_ANSWER
                    self._input_string = ''
                    continue
                elif isinstance(self._display_blocks[-1], InputAnswerDisplayBlock):
                    input_answer_display_block: InputAnswerDisplayBlock = self._display_blocks[-1]
                    if len(input_answer_display_block.input_key_combinations) > 1 \
                                and input_answer_display_block.input_key_combinations in self.hk_storage.action_hotkeys_by_key(self._action_key) \
                                and ':' not in input_answer_display_block.input_key_combinations \
                            or len(input_answer_display_block.input_key_combinations) > 1 \
                                and ':' in input_answer_display_block.input_key_combinations \
                                and ''.join(input_answer_display_block.input_key_combinations) in self.hk_storage.action_hotkeys_by_key(self._action_key) \
                            or len(input_answer_display_block.input_key_combinations) == 1 \
                                and input_answer_display_block.input_key_combinations[0] in self.hk_storage.action_hotkeys_by_key(self._action_key):
                        self._interface_state = InterfaceState.CORRECT_ANSWER
                        continue
                    else:
                        self._interface_state = InterfaceState.INCORRECT_ANSWER
                        continue
                else:
                    ValueError(f'Invalid last display block type "{type(self._display_blocks[-1])}"')
            elif self._interface_state == InterfaceState.CORRECT_ANSWER:
                self._display_blocks = [
                    DisplayBlock(ColorMode.SUCCESS,
                                 'Correct!'),
                    DisplayBlock(ColorMode.REGULAR,
                                 'Press ENTER to continue')
                ]
                self.learning_results_storage.set_action_guess_correct(self._action_key)
                self.learning_results_storage.save()
                self._interface_state = InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP
                self._next_interface_state = InterfaceState.ASKING_QUESTION
            elif self._interface_state == InterfaceState.INCORRECT_ANSWER:
                self._display_blocks = [
                    DisplayBlock(ColorMode.ERROR, 'Incorrect!'),
                    DisplayBlock(ColorMode.REGULAR, self.question_for_correct_answer),
                ]
                self.learning_results_storage.set_action_guess_wrong(self._action_key)
                self.learning_results_storage.save()
                self._interface_state = InterfaceState.CHECKING_IF_HELP_IS_NEEDED
            elif self._interface_state == InterfaceState.CHECKING_IF_HELP_IS_NEEDED:
                key = chr(k)
                if key == 'y':
                    self._interface_state = InterfaceState.SHOWING_HELP
                    continue
                elif key == 'n':
                    self._interface_state = InterfaceState.ASKING_QUESTION
                    continue
                else:
                    self._display_blocks = [
                        DisplayBlock(ColorMode.ERROR,
                                     'Invalid input, try again'),
                        DisplayBlock(ColorMode.REGULAR,
                                     self.question_for_correct_answer),
                    ]
                    self._interface_state = InterfaceState.CHECKING_IF_HELP_IS_NEEDED
            elif self._interface_state == InterfaceState.SHOWING_HELP:
                self._display_blocks = [
                    DisplayBlock(ColorMode.SUCCESS,
                                 self.help_for_action(self._action_key)),
                    DisplayBlock(ColorMode.REGULAR,
                                 'Press ENTER to continue'),
                ]
                self._interface_state = InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP
                self._next_interface_state = InterfaceState.ASKING_QUESTION
            elif self._interface_state == InterfaceState.PENDING_ENTER_TO_PROCEED_TO_NEXT_STEP:
                if k == 10:
                    self._interface_state = self._next_interface_state
                    self._next_interface_state = None
                    continue
            elif self._interface_state == InterfaceState.QUIT:
                break
            else:
                raise ValueError(f'Invalid interface state "{self._interface_state}"')

            self._render_display_blocks()

            self.window.refresh()
            k = self.window.getch()

    def _render_display_blocks(self):
        start_y = int((self._height // 2) - len(self._display_blocks) // 2)
        display_block: DisplayBlock
        cumulative_item_i = 1
        for display_block_i, display_block in enumerate(self._display_blocks):
            if '\n' in display_block.text:
                lines = display_block.text.split('\n')
            else:
                lines = (display_block.text,)
            for line_i, line in enumerate(lines):
                start_x = self._width // 2 - len(line) // 2
                self.window.addstr(start_y + cumulative_item_i, start_x, line, curses.color_pair(display_block.color_mode.value))
                cumulative_item_i += 1
