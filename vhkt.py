import logging
import sys

import vhkt.core

from pprint import pprint

logger: logging.Logger = None


def main():
    hk_storage_file_path = 'hkdb.yaml'
    hk_storage = vhkt.core.HotKeysStorage(hk_storage_file_path)
    learning_results_file_path = 'lrnres.yaml'
    learning_results = vhkt.core.LearningResultsStorage(learning_results_file_path, hk_storage)
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
    sys.exit(main())
