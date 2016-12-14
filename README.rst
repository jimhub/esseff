esseff
========================

Esseff is a simple tool for managing the deployment and versioning of AWS Step Functions
(https://aws.amazon.com/step-functions/).

You provide a directory containing .json (or .yaml) files for your state-machine
definitions and some configuration, and it does the rest!


Versioning
----------

Esseff creates state-machines using the name of the definition file (a-state-machine.yml -> 
a-state-machine) and an automatically incremented version number.

So, the first deployment of the a-state-machine.yml file will yield a state machine with the
name a-state-machine-0, and a subsequent deployment (IF the definition has changed) will yield
a-state-machine-1.

Upon successful deployment, the results of the deploy call will be written to a .deploy file of
the base name of state machine (a-state-machine.deploy) within the given directory, which
typically looks like this::

    {
        "date": "2016-12-14 11:19:45.346000-07:00",
        "name": "a-state-machine-3",
        "arn": "arn:aws:states:us-west-2:1234567890:stateMachine:a-state-machine-3"
    }


Example Execution
-----------------

Contents of some state-machines folder::

    $ ls ~/my-project/state-machines
    a-state-machine.yaml	esseff.config   some-state-machine.config     some-state-machine.json

Contents of esseff.config (base config values for all machines in directory)::

    [AWS]
    # Will default to credentials defined in environment, if these are omitted
    aws_access_key_id = {some access key}
    aws_secret_access_key = {some secret key}
    region = us-west-2

    [Machines]
    # Default execution role for the state machines
    execution-role-arn = arn:aws:iam::{some account}:role/service-role/StatesExecutionRole

Contents of some-state-machine.config (overrides values in esseff.config)::

    [Machines]
    execution-role-arn = arn:aws:iam::{some account}:role/service-role/OtherExecutionRole

Executing esseff::

    $ esseff ~/my-project/state-machines
    
    You just ran Esseff! Let's do this!
    Version: 0.0.1
    State Machine Path: ~/my-project/state-machines

    -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-

    Executing Lint Step...

    Linting a-state-machine.yaml ...
    Linting some-state-machine.json ...

    Lint Step Complete!

    -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-

    Executing Deploy Step...

    Deploying: a-state-machine.yaml
    NOP: a-state-machine code has not changed. Skipping deploy. Current version: a-state-machine-3
    Deploying: some-state-machine.json
      version: some-state-machine-0
    SUCCESS: some-state-machine-0 deployment succeeded :D

    Deploy Step Complete!

    -=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-

    Esseff is finished. Have a nice day :D

Contents of some state-machines folder after execution::

    $ ls ~/my-project/state-machines
    a-state-machine.yaml	a-state-machine.deploy  esseff.config   some-state-machine.config
    some-state-machine.deploy   some-state-machine.json

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
