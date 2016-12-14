esseff
========================

This is a structure template for Python command line applications, ready to be
released and distributed via setuptools/PyPI/pip for Python 2 and 3.

Please have a look at the corresponding article:
http://gehrcke.de/2014/02/distributing-a-python-command-line-application/


Behavior
--------

Flexible invocation
*******************

The application can be run right from the source directory, in two different
ways:

1) Treating the esseff directory as a package *and* as the main script::

    $ python -m esseff state-machine-dir

2) Using the esseff-runner.py wrapper::

    $ ./esseff-runner.py state-machine-dir

Installation sets up esseff command
**************************************

Situation before installation::

    $ esseff
    bash: esseff: command not found

Installation right from the source tree (or via pip from PyPI)::

    $ python setup.py install

Now, the ``esseff`` command is available::

    $ esseff state-machine-dir

On Unix-like systems, the installation places a ``esseff`` script into a
centralized ``bin`` directory, which should be in your ``PATH``. On Windows,
``esseff.exe`` is placed into a centralized ``Scripts`` directory which
should also be in your ``PATH``.

For Linting Support
*******************

Check if statelint installed::

    $ statelint
    bash: esseff: command not found

If not, install via instructions found here (https://github.com/awslabs/statelint)::

    $ gem install statelint

Now esseff will be able to use 'statelint' to check your state machine defs prior to deployment!
