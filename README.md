# VHKT

![](img/logo256.png)

## Intro

Vim hot keys tutor (VHKT) is (currently) console only tool to help
learn basic Vim hot keys and commands.

## Licensing

VHKT is licensed under GPL v3 or later, full license text you
can find in `LICENSE` file in repository root. 

## Requirements

To install requirements execute following commands from repository root:

    pip3 install -r requirements

Or do similar from virtualenv (if you know what it is).

## Basic Usage

Basic hot keys and commands are included to `hkdb.yaml` in repo,
feel free to use it or create your own using same syntax.

Simplest way to call VHKT is to type command from repository
directory:

    python3 vhkt.py

In this case VHKT will load `hkdb.yaml` from repository directory,
create template for learning results file with default name
`lrnres.yaml`, fill it with actions keys from `hkdb.yaml` and start
it's work.

You should see something like this (in `simple-text` mode, `curses-tui`
slightly differs):

    <517275> [2021-01-23 11:34:19,085] INFO: Hot keys storage file path not passed, using default "hkdb.yaml"
    <517275> [2021-01-23 11:34:19,114] INFO: Learning results file path not passed, using default "lrnres.yaml"
    0 action(s) learned, 11 in process, 12 guess(es), 1 error guess(es), 51 action(s) left to learn, 51 action(s) total to learn
    WHAT IS HOTKEY FOR "PASTE AFTER"?
    NOTE: Type keys combination or "\h" for help or "\e" to exit and press ENTER
    >

To learn hotkey or command you should correctly type it three times.
Mistake? Minus one, try more.

Now you could start learning, good luck!

## Advanced Usage

1. In addition to default hot keys database you could create your
own using same syntax and pass it to VHKT as first command line
argument.
1. Also you can use several different learning results files,
just pass desired path to VHKT as `-l/--learning-results-file` command
line argument and enjoy.
1. VHKT was create with intention to extend it, so if you look
at `vhkt/core.py` you will see both `Basic...` and `File...` classes.
If needed source code could be extended to work with database for
example or to support several users.

## Contacts

Feel free to submit bug reports or suggest feature requests to
VHKT main repo https://github.com/Gim6626/vhkt or directly to
me at email gim6626@gmail.com.

---

Dmitriy Vinokurov, 2020