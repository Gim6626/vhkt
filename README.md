# VHKT

## Intro

Vim hot keys tutor (VHKT) is (currently) console only tool to help
learn basic Vim hot keys and commands.

## Licensing

VHKT is licensed under GPL v3 or later, full license text you
can find in `LICENSE` file in repository root. 

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

You should see something like this:

    Learning results file path not passed, using default "lrnres.yaml"
    0 actions learned, 43 left
    What is hotkey for "Go left"?
    Type keys combination or "\h" for help or "\q" to quit:

To learn hotkey or command you should correctly type it three times.
Mistake? Minus one, try more.

Now you could start learning, good luck!

## Advanced Usage

1. In addition to default hot keys database you could create your
own using same syntax and pass it to VHKT as first command line
argument.
1. Also you can use several different learning results files,
just pass desired path to VHKT as second (optional) command line
argument and enjoy.
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