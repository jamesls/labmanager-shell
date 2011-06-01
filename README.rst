Overview
========

Labmanager Shell is a command line interface to Lab Manager's SOAP API.
It currently only supports Lab Manager's external API.


Commands
========

Below is a sample of the existing commands::

  (lmsh) list
    id   |              name              | deployed |    type    |      owner
  =======+================================+==========+============+================
  191    | TestServerOne                  | False    | workspace  | testowner1
  289    | TestServerTwo                  | True     | workspace  | testowner2
  1393   | TestServerThree                | False    | library    | testowner2


  (lmsh) machines 289
   id  |  name  |   internal    |        MAC        | memory | config
  =====+========+===============+===================+========+=======
  9601 | web1   | 172.10.10.100 | 00:50:56:0b:0e:01 | 1024   | 289
  9602 | web2   | 172.10.10.101 | 00:50:56:0b:0e:02 | 1024   | 289
  9603 | web3   | 172.10.10.102 | 00:50:56:0b:0e:03 | 1024   | 289
  9604 | db1    | 172.10.10.103 | 00:50:56:0b:0e:04 | 4096   | 289

  (lmsh) undeploy 289
  Undeploying config...
  (lmsh) deploy unfenced 289
  Deploying config...
  (lmsh)


Configuration
=============

You can either specify the configuration values via the
command line or an rc file.  For example, the following::

  $ lmsh --hostname=mylabmanager.com --username=myusername \
      --organization=myorg --workspace=myworkspace

is equivalent to this::

  $ cat > ~/.lmshrc
  [default]
  hostname=mylabmanager.com
  username=myusername
  organization=myorg
  workspace=myworkspace

  $ lmsh

Note that configuration above is in a ``default`` section.  You can
have multiple sections defined in your ~/.lmshrc and then specify
which config options to load using the ``--section`` option.

You can also specify the ``password`` option in the config file.  If
the config file does not have the ``password`` option, then you will
be prompted for your password on running ``lmsh``::

  $ lmsh
  password:
  (lmsh)


Command line options are merged with RC options, so command line options will
override configuration values.  This is useful if you want to put *your*
default values in your ``~/.lmshrc`` file.  For example, running this command
(assuming you have the above config file in ``~/.lmshrc``)::

  $ lmsh --workspace=alternate_workspace

The ``~/.lmshrc`` is first loaded, and then the workspace value is overriden
from ``myworkspace`` to ``alternate_workspace``.  The end result is that the
``hostname``, ``username``, and ``organization`` are loaded from the
``~/.lmshrc`` file and the ``workspace`` value is loaded from the value
specified on the command line.
