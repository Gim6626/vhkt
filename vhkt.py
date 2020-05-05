# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

import logging
import sys
import argparse

import vhkt.core

logger: logging.Logger = None
args = None
DEFAULT_LEARNING_RESULTS_FILE = 'lrnres.yaml'


def main():
    hk_storage_file_path = args.HOT_KEYS_STORAGE_FILE
    hk_storage = vhkt.core.FileHotKeysStorage(hk_storage_file_path)
    logger.debug('Hot keys storage loaded')
    if args.LEARNING_RESULTS_FILE:
        learning_results_file_path = args.LEARNING_RESULTS_FILE
    else:
        print(f'Learning results file path not passed, using default "{DEFAULT_LEARNING_RESULTS_FILE}"')
        learning_results_file_path = DEFAULT_LEARNING_RESULTS_FILE
    learning_results = vhkt.core.FileLearningResultsStorage(learning_results_file_path, hk_storage)
    logger.debug('Learning results storage created/loaded')
    print_learning_stats(learning_results)
    all_success = learning_results.all_actions_learned_successfully()
    if all_success:
        print('All hotkeys are learned, nothing to do')
        return 0
    while True:
        random_action_key = learning_results.random_nonlearned_action_key
        if random_action_key is None:
            continue
        question \
            = f'What is hotkey for "{hk_storage.action_description_by_key(random_action_key)}"?' \
              + f'\nType keys combination or "\\h" for help or "\\q" to quit: '
        answer = input(question)
        if answer == '\\h':
            hotkeys_str = '"' + '", "'.join(hk_storage.action_hotkeys_by_key(random_action_key)) + '"'
            print(f'Hotkey(s) for "{hk_storage.action_description_by_key(random_action_key)}": {hotkeys_str}')
        elif answer == '\\q':
            return 0
        elif answer in hk_storage.action_hotkeys_by_key(random_action_key):
            learning_results.set_action_guess_correct(random_action_key)
            print('Correct!')
        else:
            learning_results.set_action_guess_wrong(random_action_key)
            print('Wrong!')
        print_learning_stats(learning_results)
        learning_results.save()
        logger.debug('Learning results saved')
        all_success = learning_results.all_actions_learned_successfully()
        if all_success:
            print('All hotkeys are learned, nothing to do')
            return 0


def print_learning_stats(learning_results):
    print(f'{learning_results.actions_learned_count} actions learned, {learning_results.actions_to_learn_count} left')


def init_custom_logger(logging_level):
    lgr = logging.getLogger('custom_logger')

    h = logging.StreamHandler(sys.stderr)
    f = logging.Formatter('<%(process)d> [%(asctime)s] %(levelname)s: %(message)s')
    h.setFormatter(f)
    h.flush = sys.stderr.flush
    lgr.addHandler(h)
    lgr.setLevel(logging_level)

    lgr.propagate = False

    return lgr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Learn Vim hotkeys')
    parser.add_argument('HOT_KEYS_STORAGE_FILE',
                        help='Path to hot keys info storage file')
    parser.add_argument('LEARNING_RESULTS_FILE',
                        help='Path to learning results storage file',
                        nargs='?')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Debug mode')
    args = parser.parse_args()
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logger = init_custom_logger(logging_level)
    sys.exit(main())
