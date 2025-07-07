# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

from vhkt.basic import BasicTutor


class SimpleTextTutor(BasicTutor):

    def print(self, msg):
        print(msg)

    def show_help_for_action(self, action_key):
        super().show_help_for_action(action_key)
        input('Press any key to continue')

    def answer_for_question(self, question):
        answer = input(question)
        if answer == '\\h':
            answer_type = self.AnswerType.HELP
        elif answer == '\\e':
            answer_type = self.AnswerType.EXIT
        else:
            answer_type = self.AnswerType.REGULAR_ANSWER
        return answer_type, answer.split(',')

    def show_welcome_message(self):
        self.print(self.WELCOME_STRING)
        self.print(self.selected_application_string)

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
        notes.append('Type keys combination or "\\h" for help or "\\e" to exit and press ENTER')
        return notes

    def after_answer(self):
        self.print('')
