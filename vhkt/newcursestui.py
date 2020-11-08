import curses
import transitions
from typing import List, Dict
from vhkt.basic import (
    BasicTutor,
    BasicHotKeysStorage,
    BasicLearningResultsStorage,
)
from enum import Enum


class TutorState(Enum):
    HELLO = 'hello'
    GOODBYE = 'goodbye'
    STATISTICS = 'statistics'
    QUESTION = 'question'
    CORRECT_ANSWER = 'correct_answer'
    INCORRECT_ANSWER = 'incorrect_answer'
    HELP = 'help'


class TutorTransition(Enum):
    SHOW_STATISTICS = 'show_statistics'
    SAY_GOODBYE = 'say_goodbye'
    ASK_QUESTION = 'ask_question'
    SHOW_ANSWER_CORRECTNESS = 'show_answer_correctness'
    SHOW_HELP = 'show_help'


class ColorMode(Enum):
    REGULAR = 1
    STATUS_BAR = 2
    STATISTICS = 3
    QUESTION = 4
    SUCCESS = 5
    ERROR = 6


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


class NewCursesTuiTutor:

    TRANSITIONS = [
        {
            'trigger': TutorTransition.SHOW_STATISTICS.value,
            'source': TutorState.HELLO.value,
            'dest': TutorState.STATISTICS.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.STATISTICS.value,
            'dest': TutorState.GOODBYE.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.HELLO.value,
            'dest': TutorState.GOODBYE.value,
        },
        {
            'trigger': TutorTransition.ASK_QUESTION.value,
            'source': TutorState.STATISTICS.value,
            'dest': TutorState.QUESTION.value,
        },
        {
            'trigger': TutorTransition.SHOW_ANSWER_CORRECTNESS.value,
            'source': TutorState.QUESTION.value,
            'dest': TutorState.CORRECT_ANSWER.value,
        },
        {
            'trigger': TutorTransition.SHOW_HELP.value,
            'source': TutorState.QUESTION.value,
            'dest': TutorState.HELP.value,
        },
        {
            'trigger': TutorTransition.SHOW_ANSWER_CORRECTNESS.value,
            'source': TutorState.QUESTION.value,
            'dest': TutorState.INCORRECT_ANSWER.value,
        },
        {
            'trigger': TutorTransition.ASK_QUESTION.value,
            'source': TutorState.CORRECT_ANSWER.value,
            'dest': TutorState.QUESTION.value,
        },
        {
            'trigger': TutorTransition.ASK_QUESTION.value,
            'source': TutorState.INCORRECT_ANSWER.value,
            'dest': TutorState.QUESTION.value,
        },
        {
            'trigger': TutorTransition.ASK_QUESTION.value,
            'source': TutorState.HELP.value,
            'dest': TutorState.QUESTION.value,
        },
        {
            'trigger': TutorTransition.SHOW_STATISTICS.value,
            'source': TutorState.CORRECT_ANSWER.value,
            'dest': TutorState.STATISTICS.value,
        },
        {
            'trigger': TutorTransition.SHOW_STATISTICS.value,
            'source': TutorState.INCORRECT_ANSWER.value,
            'dest': TutorState.STATISTICS.value,
        },
        {
            'trigger': TutorTransition.SHOW_STATISTICS.value,
            'source': TutorState.HELP.value,
            'dest': TutorState.STATISTICS.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.CORRECT_ANSWER.value,
            'dest': TutorState.GOODBYE.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.INCORRECT_ANSWER.value,
            'dest': TutorState.GOODBYE.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.HELP.value,
            'dest': TutorState.GOODBYE.value,
        },
        {
            'trigger': TutorTransition.SAY_GOODBYE.value,
            'source': TutorState.QUESTION.value,
            'dest': TutorState.GOODBYE.value,
        },
    ]

    _EXIT_KEY = 5

    def __init__(self, hk_storage, learning_results_storage, window=None):
        self.hk_storage: BasicHotKeysStorage = hk_storage
        self.learning_results_storage: BasicLearningResultsStorage = learning_results_storage
        self._machine = transitions.Machine(self,
                                            states=[state for state in TutorState],
                                            transitions=self.TRANSITIONS,
                                            initial=TutorState.HELLO)
        self._window = window
        self._key = None
        self._display_blocks: List[DisplayBlock] = []
        self._debug_msg = None

    def _prepare(self):
        # Clear and refresh the screen for a blank canvas
        self._window.clear()
        self._window.refresh()
        # Disable cursor
        curses.curs_set(0)
        self._key = 0
        # Start colors in curses
        curses.start_color()
        for color_mode, (fg_color, bg_color) in COLOR_MODE_MAP.items():
            curses.init_pair(color_mode.value, fg_color,  bg_color)

    def _render_statistics(self):
        statistics_str = ', '.join(self._learning_stats)
        self._window.addstr(0, 0, statistics_str, curses.color_pair(ColorMode.STATISTICS.value))

    @property
    def _height(self):
        return self._window.getmaxyx()[0]

    @property
    def _width(self):
        return self._window.getmaxyx()[1]

    def _render_statusbar(self):
        self._window.attron(curses.color_pair(ColorMode.STATUS_BAR.value))
        self._window.addstr(self._height - 1, 0, self._statusbar_str)
        self._window.addstr(self._height - 1, len(self._statusbar_str), " " * (self._width - len(self._statusbar_str) - 1))
        self._window.attroff(curses.color_pair(ColorMode.STATUS_BAR.value))

    def _handle_pre_loop_iteration(self):
        self._window.clear()
        self._render_statistics()
        self._render_statusbar()

    def _handle_post_loop_iteration(self):
        self._render_display_blocks()
        self._window.refresh()
        self._key = self._window.getch()

    def _render_display_blocks(self):
        start_y = int((self._height // 2) - len(self._display_blocks) // 2)
        display_block: DisplayBlock
        for display_block_i, display_block in enumerate(self._display_blocks):
            start_x = self._width // 2 - len(display_block.text) // 2
            self._window.addstr(start_y + display_block_i, start_x, display_block.text, curses.color_pair(display_block.color_mode.value))

    @property
    def _learning_stats(self):
        stats_lines = [
            f'{self.learning_results_storage.actions_learned_count} action(s) learned',
            f'{self.learning_results_storage.actions_learning_in_process_count} in process',
            f'{self.learning_results_storage.actions_guesses_count} guess(es)',
            f'{self.learning_results_storage.actions_error_guesses_count} error guess(es)',
            f'{self.learning_results_storage.actions_to_learn_count} action(s) left to learn',
            f'{self.learning_results_storage.actions_count} action(s) total to learn',
        ]
        return stats_lines

    @property
    def _statusbar_str(self):
        s = f'Press "Ctrl+e" to exit or "Ctrl+h" for help'
        # TODO: Align debug message right
        if self._debug_msg is not None:
            s += ' | ' + self._debug_msg
        return s

    def tutor(self):
        self._prepare()
        all_success = False
        while True:
            self._handle_pre_loop_iteration()
            if self._key == self._EXIT_KEY:
                break
            if not all_success:
                self._display_blocks = [
                    DisplayBlock(ColorMode.REGULAR,
                                 'Hello!'),
                ]
            else:
                self._display_blocks = [
                    DisplayBlock(ColorMode.SUCCESS,
                                 'Congratulations, all hotkeys learned!'),
                ]
            all_success = True  # TODO: Replace with self.learning_results_storage.all_actions_learned_successfully
            self._handle_post_loop_iteration()
