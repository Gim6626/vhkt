# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

import string
import os

from vhkt.basic import BasicTutor


class CursesTextTutor(BasicTutor):

    def __init__(self, hk_storage, learning_results_storage, window):
        super().__init__(hk_storage, learning_results_storage)
        self.window = window

    def show_help_for_action(self, action_key):
        super().show_help_for_action(action_key)

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
            ignore_flag = False
            if key in string.ascii_lowercase or key in string.ascii_uppercase:
                key_modified = key
            elif len(key) == 1 and 1 <= ord(key) <= 32:
                key_modified = f'Ctrl+{string.ascii_lowercase[ord(key) - 1]}'
                last_combo = True
            elif key == 'KEY_BACKSPACE':
                if len(answer_blocks) > 0:
                    self.print('\b \b', newline=False)
                    del answer_blocks[-1]
                key_modified = ''
                ignore_flag = True
            elif key in ['KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT']:
                key_modified = ''
                ignore_flag = True
            else:
                key_modified = key

            if not ignore_flag:
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
            answer_type = self.AnswerType.EXIT
        else:
            answer_type = self.AnswerType.REGULAR_ANSWER
        answer_blocks = answer_blocks[:-1]
        if len(answer_blocks) > 1 and answer_blocks[0] == ':':
            s = ''
            for c in answer_blocks:
                s += c
            answer_blocks = [s]
        return answer_type, answer_blocks

    def before_success(self):
        self.window.clear()

    def before_question(self):
        self.window.clear()

    def after_answer(self):
        self.print('Press any key to continue')
        self.window.getkey()
