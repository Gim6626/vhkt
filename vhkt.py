# Copyleft GPLv3 or later
# 2020 Dmitriy Vinokurov gim6626@gmail.com

import logging
import sys
import argparse
import curses
from pathlib import Path

import vhkt.basic
import vhkt.cursestext
import vhkt.cursestui
import vhkt.filestorage
import vhkt.simpletext

logger: logging.Logger = None
args = None


def main(window=None):
    hk_storage, learning_results_storage = init_storages()
    tutor: vhkt.basic.BasicTutor
    if args.interface_mode == vhkt.basic.InterfaceMode.SIMPLE_TEXT:
        tutor = vhkt.simpletext.SimpleTextTutor(hk_storage, learning_results_storage)
    elif args.interface_mode == vhkt.basic.InterfaceMode.CURSES_TEXT:
        tutor = vhkt.cursestext.CursesTextTutor(hk_storage, learning_results_storage, window)
    elif args.interface_mode == vhkt.basic.InterfaceMode.CURSES_TUI:
        tutor = vhkt.cursestui.CursesTuiTutor(hk_storage, learning_results_storage, args.answer_mode, window)
    else:
        raise NotImplementedError(f'Invalid interface mode "{args.interface_mode}"')
    tutor.tutor()


def init_storages():
    hk_storage_file_path = Path(args.APP_HOT_KEYS_STORAGE_FILE)
    hk_storage = vhkt.filestorage.FileHotKeysStorage(hk_storage_file_path)
    logger.debug('Hot keys storage loaded')

    if args.learning_results_file:
        learning_results_file_path = Path(args.learning_results_file)
    else:
        learning_results_file_path = hk_storage_file_path.parent / f'.results-for-{hk_storage_file_path.stem}.yaml'
        logger.info(f'Learning results file path not passed, using "{learning_results_file_path}"')
    learning_results_storage = vhkt.filestorage.FileLearningResultsStorage(learning_results_file_path, hk_storage)
    if not args.learning_results_file:
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
    parser = argparse.ArgumentParser(description='Learn hotkeys for popular programs')
    parser.add_argument('APP_HOT_KEYS_STORAGE_FILE',
                        help='Path to application hot keys info storage file')
    parser.add_argument('-l',
                        '--learning-results-file',
                        help='Path to learning results storage file',
                        nargs='?')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Debug mode')
    parser.add_argument('-i',
                        '--interface-mode',
                        choices=[m.value for m in vhkt.basic.InterfaceMode],
                        default=vhkt.basic.InterfaceMode.CURSES_TUI,
                        help=f'Interface mode. Currently only "{vhkt.basic.InterfaceMode.CURSES_TUI.value}" is actively developed, others considered obsolete and planned for removal in future.')
    parser.add_argument('-a',
                        '--answer-mode',
                        choices=[m.value for m in vhkt.basic.AnswerMode],
                        default=vhkt.basic.AnswerMode.SELECT,
                        help=f'Answer mode. Currently only "{vhkt.basic.AnswerMode.SELECT.value}", meaning select hot key from options, is supported. "{vhkt.basic.AnswerMode.INPUT}" mode, i.e. enter hot key directly, is not actively supported and may be considered deprecated and removed in future.')
    global args
    args = parser.parse_args()
    args.interface_mode = vhkt.basic.InterfaceMode(args.interface_mode)
    args.answer_mode = vhkt.basic.AnswerMode(args.answer_mode)


if __name__ == '__main__':
    init_args()
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logger = init_custom_logger(logging_level)
    if args.interface_mode == vhkt.basic.InterfaceMode.SIMPLE_TEXT:
        main()
    else:
        curses.wrapper(main)
