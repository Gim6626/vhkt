# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

import logging
import sys
import argparse
import curses

import vhkt.basic

logger: logging.Logger = None
args = None
DEFAULT_LEARNING_RESULTS_FILE = 'lrnres.yaml'


def main(window=None):
    hk_storage, learning_results_storage = init_storages()
    tutor: vhkt.basic.BasicTutor
    if args.mode == vhkt.basic.Mode.SIMPLE_TEXT:
        tutor = vhkt.simpletext.SimpleTextTutor(hk_storage, learning_results_storage)
    elif args.mode == vhkt.basic.Mode.CURSES_TEXT:
        tutor = vhkt.cursestext.CursesTextTutor(hk_storage, learning_results_storage, window)
    elif args.mode == vhkt.basic.Mode.CURSES_TUI:
        tutor = vhkt.cursestui.CursesTuiTutor(hk_storage, learning_results_storage, window)
    else:
        raise NotImplementedError(f'Interface mode "{args.mode}" not supported yet')
    tutor.tutor()


def init_storages():
    hk_storage_file_path = args.HOT_KEYS_STORAGE_FILE
    hk_storage = vhkt.filestorage.FileHotKeysStorage(hk_storage_file_path)
    logger.debug('Hot keys storage loaded')
    if args.LEARNING_RESULTS_FILE:
        learning_results_file_path = args.LEARNING_RESULTS_FILE
    else:
        print(f'Learning results file path not passed, using default "{DEFAULT_LEARNING_RESULTS_FILE}"')
        learning_results_file_path = DEFAULT_LEARNING_RESULTS_FILE
    learning_results_storage = vhkt.filestorage.FileLearningResultsStorage(learning_results_file_path, hk_storage)
    if not args.LEARNING_RESULTS_FILE:
        learning_results_storage.save()
    return hk_storage, learning_results_storage


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


def init_args():
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
    parser.add_argument('-m',
                        '--mode',
                        choices=[m.value for m in vhkt.basic.Mode],
                        default=vhkt.basic.Mode.CURSES_TEXT,
                        help='Interface mode')
    global args
    args = parser.parse_args()
    args.mode = vhkt.basic.Mode(args.mode)


if __name__ == '__main__':
    init_args()
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logger = init_custom_logger(logging_level)
    if args.mode == vhkt.basic.Mode.SIMPLE_TEXT:
        sys.exit(main())
    else:
        curses.wrapper(main)
