Contributing
============

The code repository is located at `OpenStack <https://github.com/openstack>`__.
Please go there if you want to check it out:

    git clone https://github.com/openstack/watcher-dashboard.git

The list of bugs and blueprints is on Launchpad:

`<https://launchpad.net/watcher-dashboard>`__

We use OpenStack's Gerrit for the code contributions:

`<https://review.opendev.org/#/q/status:open+project:openstack/watcher-dashboard,n,z>`__

and we follow the `OpenStack Gerrit Workflow <https://docs.openstack.org/infra/manual/developers.html#development-workflow>`__.

If you're interested in the code, here are some key places to start:

* `watcher_dashboard/api.py <https://github.com/openstack/watcher-dashboard/blob/master/watcher_dashboard/api.py>`_
  - This file contains all the API calls made to the Watcher API
  (through python-watcherclient).
* `watcher_dashboard/infra_optim <https://github.com/openstack/watcher-dashboard/tree/master/watcher_dashboard/infra_optim>`_
  - The Watcher Dashboard code is contained within this directory.

Running tests
=============

There are several ways to run tests for watcher-dashboard.

Using ``tox``:

    This is the easiest way to run tests. When run, tox installs dependencies,
    prepares the virtual python environment, then runs test commands. The gate
    tests in gerrit usually also use tox to run tests. For available tox
    environments, see ``tox.ini``.

By running ``run_tests.sh``:

    Tests can also be run using the ``run_tests.sh`` script, to see available
    options, run it with the ``--help`` option. It handles preparing the
    virtual environment and executing tests, but in contrast with tox, it does
    not install all dependencies, e.g. ``jshint`` must be installed before
    running the jshint testcase.

Manual tests:

    To manually check watcher-dashboard, it is possible to run a development server
    for watcher-dashboard by running ``run_tests.sh --runserver``.

    To run the server with the settings used by the test environment:
    ``run_tests.sh --runserver 0.0.0.0:8000``

OpenStack Style Commandments
============================

- Step 1: Read https://www.python.org/dev/peps/pep-0008/
- Step 2: Read https://www.python.org/dev/peps/pep-0008/ again
- Step 3: Read https://github.com/openstack/hacking/blob/master/HACKING.rst
