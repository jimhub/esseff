esseff
========================

Esseff is a simple tool for management the deployment and versioning of AWS Step Functions
(https://aws.amazon.com/step-functions/).

You provide a directory containing .json (or .yaml) files for your state-machine
definitions and some configuration, and it does the rest!


Example
-------

    $ ls ~/my-project/state-machines
    a-state-machine.yaml	esseff.config   some-state-machine.json     some-state-machine.config

Contents of esseff.config (base config values for all machines in directory)::

    [AWS]
    # Will default to ~/.aws/credentials if omitted
    aws_access_key_id = {some access key}
    aws_secret_access_key = {some secret key}
    region = us-west-2

    [Machines]
    # Default execution role for the state machines
    execution-role-arn = arn:aws:iam::{some account}:role/service-role/StatesExecutionRole

Contents of some-state-machine.config (overrides values in esseff.config)::

    [Machines]
    execution-role-arn = arn:aws:iam::{some account}:role/service-role/OtherExecutionRole

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
    bash: statelint: command not found

If not, install via instructions found here (https://github.com/awslabs/statelint)::

    $ gem install statelint

Now esseff will be able to use 'statelint' to check your state machine defs prior to deployment!
