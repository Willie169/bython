# Bython
Python with braces. Because Python is awesome, but whitespace is awful.

Bython is a Python preprocessor that translates curly brackets into indentation and converts Bython code to Python code.

## Content of README:
  * [Key features](#key-features)
  * [Code example](#code-example)
  * [Installation](#installation)
  * [Quick intro](#quick-intro)
  * [Structure of the repository](#structure-of-the-repository)

## Key features

* "Forget" about indentation. You should still write beautiful code, but if you mess up with tabs/spaces, or copy one piece of code to another that uses a different indentation style, it won't break.
* Converts C-style variable declarations and function signatures to Python.
* Supports converting comments from C-style to Python-style.
* Handles file imports and changes filenames from `.by` to `.py`.

## Code example

```python
def print_message(num_of_times):  # Converted from Bython
    for i in range(num_of_times):
        print("Bython is awesome!")

if __name__ == "__main__":
    print_message(10)
```

## Installation

You can install Bython directly from PyPI using pip (with or without `sudo -H`, depending on your Python installation):

```
$ sudo -H pip3 install bython
```

If you prefer to install it from the Git repository, you can use `git clone` and do a local install:

```
$ git clone https://github.com/mathialo/bython.git
$ cd bython
$ sudo -H pip3 install .
```

The Git version is sometimes slightly ahead of the PyPI version.

To uninstall, run:

```
$ sudo pip3 uninstall bython
```

which will undo all the changes.

## Quick intro

Bython works by first translating Bython files (suggested file extension: `.by`) into Python files and then using Python to run them. You need a working installation of Python for Bython to work.

To run a Bython program, simply type:

```
$ bython source.by arg1 arg2 ...
```

to run `source.by` with `arg1`, `arg2`, ... as command-line arguments. For more details on running Bython files (flags, etc.), type:

```
$ bython -h
```

to print the built-in help page. You can also consult the man page by typing:

```
$ man bython
```

Bython includes a translator from Python to Bython, found via the `py2by` command:

```
$ py2by test.py
```

This creates a Bython file called `test.by`. For a full explanation of `py2by`, type:

```
$ py2by -h
```

or consult the man page:

```
$ man py2by
```

For a more in-depth introduction, consult the [Bython introduction](INTRODUCTION.md).

## Structure of the repository

The Bython repository is structured into the following directories:

* `bython` contains the Python package with the parser and other utilities used by the main script.
* `etc` contains manual pages and other auxiliary files.
* `scripts` contains runnable Python scripts, i.e., the ones run from the shell.
* `testcases` contains sample `.by` and `.py` files intended for testing the implementation.
