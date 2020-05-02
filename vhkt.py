import logging
import sys
import yaml
import os.path
from typing import Dict
import random

import vhkt.core

from pprint import pprint

logger: logging.Logger = None


def main():
    db = vhkt.core.HotKeysDataBase('hkdb.yaml')
    learning_results_file_path = 'lrnres.yaml'
    learning_results: Dict = {}
    if os.path.isfile(learning_results_file_path):
        with open(learning_results_file_path, 'r') as learning_results_file:
            learning_results_data = learning_results_file.read()
            learning_results = yaml.safe_load(learning_results_data)
    else:
        learning_results = {'actions': {}}
    all_success = all_actions_learned_successfully(learning_results)
    if all_success:
        print('All hotkeys are learned, nothing to do')
        return 0
    while True:
        db_actions_keys = list(db.actions.keys())
        random_action_key_index = random.randint(0, len(db_actions_keys) - 1)
        random_action_key = db_actions_keys[random_action_key_index]
        if random_action_key in learning_results['actions'] \
                and 'success' in learning_results['actions'][random_action_key] \
                and learning_results['actions'][random_action_key]['success']:
            continue
        if random_action_key not in learning_results['actions']:
            learning_results['actions'][random_action_key] = {}
        current_action = db.actions[random_action_key]
        question = f'What is hotkey for "{current_action["description"]}"? '
        hotkey = input(question)
        if hotkey in current_action['hotkeys']:
            learning_results['actions'][random_action_key]['success'] = True
        with open(learning_results_file_path, 'w') as learning_results_file:
            learning_results_file_data = yaml.safe_dump(learning_results)
            learning_results_file.write(learning_results_file_data)
        all_success = all_actions_learned_successfully(learning_results)
        if all_success:
            print('All hotkeys are learned, nothing to do')
            return 0


def all_actions_learned_successfully(learning_results):
    all_success = True
    if learning_results['actions'] == {}:
        all_success = False
    else:
        for action_key, action_value in learning_results['actions'].items():
            if 'success' in learning_results['actions'][action_key] \
                    and not learning_results['actions'][action_key]['success'] \
                    or action_key not in learning_results['actions'] \
                    or 'success' not in learning_results['actions'][action_key]:
                all_success = False
    return all_success


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
