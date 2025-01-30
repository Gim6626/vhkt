# VHKT

![](img/logo256.png)

## Intro

Vim Hotkeys Tutor (VHKT) is a console tool designed to assist in learning
basic Vim hotkeys and commands.

## Requirements

To install the required packages, execute the following command from the root
of the repository

    $ pip3 install -r requirements.txt

or do something similar from within a virtual environment.

## Basic Usage

Basic hotkeys and commands are included in the hkdb.yaml file in the
repository. Feel free to use it or create your own using the same syntax.

The simplest way to call VHKT is to type the command from the repository
directory:

    $ python3 vhkt.py

In this case, VHKT will load `hkdb.yaml` from the repository directory, create
a template for the learning results file with the default name `lrnres.yaml`,
populate it with action keys from `hkdb.yaml`, and start its work.

You should see something like this (in `simple-text` mode; `curses-tui` is
slightly different):

    <517275> [2021-01-23 11:34:19,085] INFO: Hot keys storage file path not passed, using default "hkdb.yaml"
    <517275> [2021-01-23 11:34:19,114] INFO: Learning results file path not passed, using default "lrnres.yaml"
    0 action(s) learned, 11 in process, 12 guess(es), 1 error guess(es), 51 action(s) left to learn, 51 action(s) total to learn
    WHAT IS HOTKEY FOR "PASTE AFTER"?
    NOTE: Type keys combination or "\h" for help or "\e" to exit and press ENTER
    >

To learn a hotkey or command, you need to type it correctly three times.
Made a mistake? That's minus one, try again.

Now you can start learning. Good luck!


## Advanced Usage

1. In addition to the default hotkeys database, you can create your own using
   the same syntax and pass it to VHKT as the first command-line argument.
2. You can also use several different learning results files. Just pass the
   desired path to VHKT as the `-l/--learning-results-file` command-line
   argument and enjoy.
3. VHKT was created with the intention of being extendable. If you look at
   `vhkt/core.py`, you will see both `Basic...` and `File...` classes. If
   needed, the source code can be extended to work with a database, for
   example, or to support multiple users.
