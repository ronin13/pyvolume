=============================== PyVolume ===============================

|Build Status| |Coverage Status| |Updates| |Python 3|

|python| |docker|

Python Docker Volume driver.

Supports pluggable implementations, currently there are three written.

Implements: \* '/Plugin.Activate' \* '/VolumeDriver.Create' \*
'/VolumeDriver.Remove' \* '/VolumeDriver.List' \* '/VolumeDriver.Path'
\* '/VolumeDriver.Mount' \* '/VolumeDriver.Unmount' \*
'/VolumeDriver.Get' \* '/VolumeDriver.Capabilities'

for `Docker
Volume <https://docs.docker.com/engine/extend/plugins_volume/>`__.

and \* '/' \* '/shutdown'

for management.

The volume manager (common to all drivers) uses
`Flask <http://flask.pocoo.org/>`__ for routing and handles multiple
invocations of Mount and Unmount for same volume as per docker
specifications. It also passes options passed through API to the
drivers. Cleanup is also handled on shutdown.

Current Implementations
~~~~~~~~~~~~~~~~~~~~~~~

|Zookeeper| |Openssh|

-  `Ephemeral FileSystem <pyvolume/local.py>`__
-  `SSHFS FileSystem <pyvolume/sshfs.py>`__
-  `Zookeeper FileSystem <pyvolume/zkfuse.py>`__

   -  This uses
      `docker-zkfuse <https://github.com/ronin13/docker-zkfuse>`__ for
      using
      `zkfuse <https://github.com/apache/zookeeper/tree/master/src/contrib/zkfuse>`__
      and mounts zkfuse from container to host through shared mounting
      of volume from host to container.

Installing
----------

1. Install the package.

::


    pip install -r requirements.txt --user
    python2 setup.py install --prefix=/usr/local

After this pyvolume should be available as /usr/local/bin/pyvolume.

2. Copy the pyvolume.json to /etc/docker/plugins/

Dependencies:
~~~~~~~~~~~~~

Installation
~~~~~~~~~~~~

1. Python 2.7 and python related dependencies - pip, virtualenv etc.
2. sshfs for SSHFileSystem (default).

Integration Testing Dependencies.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. ssh-add and sshfs.
2. curl
3. util-linux (for mount etc.)
4. Python-related tools such as virtualenv.

Usage
-----

Permissions
^^^^^^^^^^^

-  Make sure you have write permissions for base mount directory which
   is /mnt by default.

   -  If not, make sure to chown as the user you run pyvolume as.

-  For ZookeeperFileSystem, make sure the pyvolume's user can do docker
   run without sudo.

   -  If not, add the pyvolume's user to docker group.

For SSH FileSystem
^^^^^^^^^^^^^^^^^^

Arguments for docker volume create:

-  remote\_path: as host:directory (Required)
-  ssh\_config: path to ssh config directory if it is not default.
-  sshfs\_options: any options to pass to sshfs.

After Installing,

1. Make sure the ssh keys are available through the ssh-agent.

::

    ssh-add -l

2. Start the pyvolume server.

::

        $ /usr/local/bin/pyvolume
        INFO:werkzeug: * Running on http://0.0.0.0:1331/ (Press CTRL+C to quit)

3. Create a docker volume.

::

        docker volume create -d pyvolume --name myvolume2 -o 'remote_path=server:/home/user' -o 'ssh_config=/home/rprabhu/.ssh.bkp/config.server'

4. Run docker as usual, providing the newly created volume name.

::

       docker run -it -v myvolume2:/data  busybox:latest sh

5. PROFIT!

For ZooKeeper FileSystem
^^^^^^^^^^^^^^^^^^^^^^^^

Arguments for docker volume create:

-  zookeeper\_string - host:port (or a list of tuples) to running
   zookeeper instance. (Required)
-  docker\_opt - any options to pass to docker.

1. Start the pyvolume server.

::

        $ /usr/local/bin/pyvolume -t zookeeper
        INFO:werkzeug: * Running on http://0.0.0.0:1331/ (Press CTRL+C to quit)

3. Create a docker volume.

::

        docker volume create -d pyvolume --name zoo -o 'zookeeper_string=0.0.0.0:2181' -o 'docker_opt=--net=host'

This assumes that you have a local zookeeper running on host at
0.0.0.0:2181. Since it is running on host, you need '--net=host' as
well.

Otherwise, if you have zookeeper running on :math:`host:`\ port,
following will do:

::

        docker volume create -d pyvolume --name zoo -o "zookeeper_string=$host:$port"

4. Run docker as usual, providing the newly created volume name.

::

       docker run -it -v zoo:/data  busybox:latest sh

and you can access the zookeeper znodes through /data/ after this.

Local Installation and Running
------------------------------

1. Look above for dependencies.
2. 

::

        $ make devenv
        $ source devenv/bin/activate

        $ ./devenv/bin/pyvolume --help

        usage: pyvolume [-h] [-t {sshfs,ephemeral}] [-H HOST] [-p PORT] [-m BASE]

        Arguments to volume router

        optional arguments:
        -h, --help            show this help message and exit
        -t {sshfs,ephemeral}, --driver {sshfs,ephemeral}
                                Type of driver to use
        -H HOST, --host HOST  Host to listen on
        -p PORT, --port PORT  Port to listen on
        -m BASE, --base BASE  Base directory to mount over

        $ ./devenv/bin/pyvolume
        INFO:werkzeug: * Running on http://0.0.0.0:1331/ (Press CTRL+C to quit)

Testing
-------

Integration test.
~~~~~~~~~~~~~~~~~

1. Set the required environment variables.

::

       a. export SSH_CONFIG=/home/rprabhu/.ssh.bkp/config.server
       b. export REMOTE_PATH='server:/home/user'
       c. make itest

2. itest log -
   https://gist.github.com/ronin13/83d99b801202e63f07523c1c5b2be450

Unit test.
~~~~~~~~~~

1. make test

::

        make test
        tox2 -e py27
        GLOB sdist-make: /home/rprabhu/repo/pyvolume/setup.py
        py27 create: /home/rprabhu/repo/pyvolume/.tox/py27
        py27 installdeps: -r/home/rprabhu/repo/pyvolume/requirements_dev.txt
        py27 inst: /home/rprabhu/repo/pyvolume/.tox/dist/pyvolume-0.1.0.zip
        py27 installed: You are using pip version 8.1.2, however version 9.0.0 is available.,You should consider upgrading via the 'pip install --upgrade pip' command.,alabaster==0.7.9,argh==0.26.2,Babel==2.3.4,bumpversion==0.5.3,cffi==1.8.3,click==6.6,coverage==4.1,cryptography==1.4,docutils==0.12,enum34==1.1.6,flake8==2.6.0,Flask==0.11.1,idna==2.1,imagesize==0.7.1,ipaddress==1.0.17,itsdangerous==0.24,Jinja2==2.8,MarkupSafe==0.23,mccabe==0.5.2,pathtools==0.1.2,pluggy==0.3.1,plumbum==1.6.2,py==1.4.31,pyasn1==0.1.9,pycodestyle==2.0.0,pycparser==2.17,pyflakes==1.2.3,Pygments==2.1.3,pytest==2.9.2,pytz==2016.7,pyvolume==0.1.0,PyYAML==3.11,six==1.10.0,snowballstemmer==1.2.1,Sphinx==1.4.8,tox==2.3.1,virtualenv==15.0.3,watchdog==0.8.3,Werkzeug==0.11.11
        py27 runtests: PYTHONHASHSEED='2628874551'
        py27 runtests: commands[0] | pip install -U pip
        Collecting pip
        Using cached pip-9.0.0-py2.py3-none-any.whl
        Installing collected packages: pip
        Found existing installation: pip 8.1.2
            Uninstalling pip-8.1.2:
            Successfully uninstalled pip-8.1.2
        Successfully installed pip-9.0.0
        py27 runtests: commands[1] | py.test
        ==================================================================================================== test session starts ====================================================================================================
        platform linux2 -- Python 2.7.12, pytest-2.9.2, py-1.4.31, pluggy-0.3.1
        rootdir: /home/rprabhu/repo/pyvolume, inifile: tox.ini
        collected 3 items

        test_pyvolume_sshfs.py ...

        ================================================================================================= 3 passed in 0.09 seconds ==================================================================================================
        __________________________________________________________________________________________________________ summary __________________________________________________________________________________________________________
        py27: commands succeeded
        congratulations :)

License
-------

-  Free software: MIT license

Credits
-------

This package was created with Cookiecutter\_ and the
'audreyr/cookiecutter-pypackage' project template.

-  Cookiecutter: https://github.com/audreyr/cookiecutter
-  audreyr/cookiecutter-pypackage:
   https://github.com/audreyr/cookiecutter-pypackage

.. |Build Status| image:: https://travis-ci.org/ronin13/pyvolume.svg?branch=master
   :target: https://travis-ci.org/ronin13/pyvolume
.. |Coverage Status| image:: https://coveralls.io/repos/github/ronin13/pyvolume/badge.svg?branch=master
   :target: https://coveralls.io/github/ronin13/pyvolume?branch=master
.. |python| image:: images/python.png
.. |docker| image:: images/docker-whale.png
.. |Zookeeper| image:: https://www.dropbox.com/s/7vmgl4mo9qvlncp/zookeeper.png?dl=1
.. |Openssh| image:: https://www.dropbox.com/s/8v7e8cu1wcwcipr/openssh.jpg?dl=1
