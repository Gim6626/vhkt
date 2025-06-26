# VHKT

![](img/logo256.png)

## Intro

VHKT Hotkeys Tutor is a console tool designed to assist in learning
basic hotkeys and commands for popular applications.

## Requirements

To install the required packages, execute the following command from the root
of the repository

    $ pip3 install -r requirements.txt

or do something similar from within a virtual environment.

## Basic Usage

Basic hotkeys and commands are described in YAML files in the `hotkeys/` 
directory of the repository. Feel free to use it or create your own using
the same syntax.

The simplest way to call VHKT is to type the command from the repository
directory:

    $ python3 vhkt.py hotkeys/SOME_APP.yaml

In this case, VHKT will load the specified file, create a blank file with
learning results file with name `.results-for-SOME_APP.yaml`, populate it with
action keys from the hotkeys file, and start its work.

You should see something like this (in `simple-text` mode; `curses-tui` is
slightly different):

```
<211161> [2025-06-26 23:01:43,743] INFO: Learning results file path not passed, generating new one in hotkeys/.results-for-bash.yaml
0 action(s) learned, 0 in process, 0 guess(es), 0 error guess(es), 15 action(s) left to learn, 15 action(s) total to learn
WHAT IS HOTKEY FOR "PLACE CURRENT PROCESS IN BACKGROUND"?
NOTES:
1. If you need to use Ctrl or other special key in answer, type it's name plus regular key like "Ctrl+w"
2. Type keys combination or "\h" for help or "\e" to exit and press ENTER
>
```

To learn a hotkey or command, you need to type it correctly three times.
Made a mistake? That's minus one, try again.

Now you can start learning. Good luck!


## Advanced Usage

1. In addition to the default applications hotkeys databases, you can create
   your own using the same syntax and pass it to VHKT as the first
   command-line argument.
2. You can also use several different learning results files. Just pass the
   desired path to VHKT as the `-l/--learning-results-file` command-line
   argument and enjoy.
3. VHKT was created with the intention of being extendable. If you look at
   `vhkt/core.py`, you will see both `Basic...` and `File...` classes. If
   needed, the source code can be extended to work with a database, for
   example, or to support multiple users.
