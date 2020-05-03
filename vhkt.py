import logging
import sys
import argparse

import vhkt.core

from pprint import pprint

logger: logging.Logger = None
args = None


def main():
    hk_storage_file_path = args.HOT_KEYS_STORAGE_FILE
    hk_storage = vhkt.core.FileHotKeysStorage(hk_storage_file_path)
    learning_results_file_path = args.LEARNING_RESULTS_FILE
    learning_results = vhkt.core.FileLearningResultsStorage(learning_results_file_path, hk_storage)
    all_success = learning_results.all_actions_learned_successfully()
    if all_success:
        print('All hotkeys are learned, nothing to do')
        return 0
    while True:
        random_action_key = learning_results.random_nonlearned_action_key
        if random_action_key is None:
            continue
        question = f'What is hotkey for "{hk_storage.action_description_by_key(random_action_key)}"? '
        hotkey = input(question)
        if hotkey in hk_storage.action_hotkeys_by_key(random_action_key):
            learning_results.set_action_learned_success(random_action_key)
            print('Correct!')
        else:
            print('Wrong!')
        learning_results.save()
        all_success = learning_results.all_actions_learned_successfully()
        if all_success:
            print('All hotkeys are learned, nothing to do')
            return 0


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
    logger = init_custom_logger(logging.DEBUG)
    parser = argparse.ArgumentParser(description='Learn Vim hotkeys')
    parser.add_argument('HOT_KEYS_STORAGE_FILE',
                        help='Path to hot keys info storage file')
    parser.add_argument('LEARNING_RESULTS_FILE',
                        help='Path to learning results storage file')
    args = parser.parse_args()
    sys.exit(main())
