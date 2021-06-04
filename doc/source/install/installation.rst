Installation
------------


First off, create a virtual environment and install the Horizon dependencies::

    $ git clone https://github.com/openstack/horizon
    $ cd horizon
    $ python tools/install_venv.py

We will refer to the folder you are now in as ``<HORIZON_DIR>``.
If you want more details on how to install Horizon, you can have a look at the
`Horizon documentation`_, especially their `quickstart tutorial`_.

Then, you need to install Watcher Dashboard on the server running Horizon.
To do so, you can issue the following commands::

    $ git clone https://opendev.org/openstack/watcher-dashboard
    $ cd watcher-dashboard
    $ pip install -e .

We will refer to the folder you are now in as ``<DASHBOARD_DIR>``.

The next step is now to register the Watcher Dashboard plugins against your
Horizon. To do so, you can execute the ``tools/register_plugin.sh``::

    $ cd <DASHBOARD_DIR>
    $ ./tools/register_plugin.sh . <HORIZON_DIR>

This script will then create the needed symlinks within Horizon so that it can
load the Watcher plugin when it starts.

If you wish to have Horizon running being an Apache server, do not forget to
start the service via the following command::

    $ sudo service apache2 restart

For more details on how to configure Horizon for a production environment, you
can refer to their online `installation guide`_.

.. _Horizon documentation: https://docs.openstack.org/horizon/latest
.. _quickstart tutorial: https://docs.openstack.org/horizon/latest/contributor/quickstart.html
.. _installation guide: https://docs.openstack.org/horizon/latest/install/index.html


DevStack setup
--------------

Add the following to your DevStack ``local.conf`` file

::

    enable_plugin watcher-dashboard https://opendev.org/openstack/watcher-dashboard


Unit testing
------------

First of all, you have to create an environment to run your tests in. This step
is actually part of the ``run_tests.sh`` script which creates and maintains a
clean virtual environment.

Here below is the basic command to run Watcher Dashboard tests::

    $ ./run_tests.sh

The first time you will issue the command above, you will be asked if you want
to create a virtual environment. So unless you have installed everything
manually (in which case you should use the ``-N`` flag), you need to accept


Integration testing
-------------------

Before being able to run integration tests, you need to have a Horizon server
running with Watcher Dashboard plugin configured. To do so, you can run a test
server using the following command::

    $ ./run_tests.sh --runserver 0.0.0.0:8000

By default, integration tests expect to find a running Horizon server at
``http://localhost:8000/`` but this can be customized by editing the
``watcher_dashboard/test/integration_tests/horizon.conf`` configuration file.
Likewise, this Horizon will be looking, by default, for a Keystone backend at
``http://localhost:5000/v2.0``. So in order to customize its location, you will
have to edit ``watcher_dashboard/test/settings.py`` by updating the
``OPENSTACK_KEYSTONE_URL`` variable.

To run integration tests::

    $ ./run_tests.sh --integration

You can use PhantomJS as a headless browser to execute your integration tests.
On an Ubuntu distribution you can install it via the following command::

    $ sudo apt-get install phantomjs

Then you can run your integration tests like this::

    $ ./run_tests.sh --integration --selenium-headless

Please note that these commands are also available via ``tox``.

.. note::

    As of the Mitaka release, the dashboard for watcher is now maintained
    outside of the Horizon codebase, in this repository.


Policies
--------
You can enable policies on Watcher ``Optimization`` panel, by updating in the
``<HORIZON_DIR>/openstack_dashboard/settings.py`` configuration file the
following parameters

    POLICY_FILES = {
    ...
    'infra-optim': 'watcher_policy.json',
    }

You can also update the file ``<HORIZON_DIR>/openstack_dashboard/conf/watcher_policy.conf``
to customize your policies.


Links
-----

Watcher project: https://opendev.org/openstack/watcher/

Watcher at github: https://github.com/openstack/watcher

Watcher at wiki.openstack.org: https://wiki.openstack.org/wiki/Watcher

Launchpad project: https://launchpad.net/watcher

Join us on IRC (Internet Relay Chat)::

    Network: OFTC (https://www.oftc.net/)
    Channel: #openstack-watcher

Or send an email to openstack-discuss@lists.openstack.org using [watcher] in object
