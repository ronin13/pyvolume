===============================
PyVolume
===============================

Python Docker Volume driver.

Supports pluggable implementations.
Uses Flask for routing.

Implements:
    '/Plugin.Activate'
    '/VolumeDriver.Create'
    '/VolumeDriver.Remove'
    '/VolumeDriver.List'
    '/VolumeDriver.Path'
    '/VolumeDriver.Mount'
    '/VolumeDriver.UnMount'
    '/VolumeDriver.Get'
    '/VolumeDriver.Capabilities'

for Docker Volume 

and 
    '/'
    '/shutdown'

for management.

* Free software: MIT license

Installing
-----------
1. Install the package. 

```
    pip install -r requirements.txt --user
    python2 setup.py install --prefix=/usr/local
```

After this pyvolume should be available as /usr/local/bin/pyvolume.

2. Copy the pyvolume.json to /etc/docker/plugins/

### Dependencies:

### Installation
1. Python 2.7 and python related dependencies - pip, virtualenv etc.
2. sshfs for SSHFileSystem (default).

#### Integration Testing Dependencies.
1. ssh-add and sshfs.
2. curl
3. util-linux (for mount etc.)
4. Python-related tools such as virtualenv.

Running
-------

After Installing, 

1. Start the pyvolume server.

```
    $ /usr/local/bin/pyvolume
    INFO:werkzeug: * Running on http://0.0.0.0:1331/ (Press CTRL+C to quit)
    
```

1. Create a docker volume.

```
    docker volume create -d pyvolume --name myvolume2 -o 'remote_path=server:/home/user' -o 'ssh_config=/home/rprabhu/.ssh.bkp/config.server'
```

2. Run docker as usual, providing the newly created volume name.

```
   docker run -it -v myvolume2:/data  busybox:latest sh
```

3. PROFIT!

Local Installation and Running
-------
1. Look above for dependencies.
2. 

```
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
```


Testing
----------

### Integration test.

1. Set the required environment variables.

```
   a. export SSH_CONFIG=/home/rprabhu/.ssh.bkp/config.server
   b. export REMOTE_PATH='server:/home/user'
   c. make itest
```

2. itest log - https://gist.github.com/ronin13/83d99b801202e63f07523c1c5b2be450

### Unit test.

1. make test

```
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
```


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

