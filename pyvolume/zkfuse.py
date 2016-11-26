# -*- coding: utf-8 -*-
""" Module providing ZKFileSystem implementation."""
from __future__ import unicode_literals

import logging
import os
import os.path

from plumbum import ProcessExecutionError

from pyvolume.exceptions import NeedOptionsException

log = logging.getLogger(__name__)

try:
    from plumbum.cmd import docker
except ImportError:
    log.warning("This can be ignored during testing or on travis")

DOCKER_IMAGE = "ronin/zkfuse:latest"
CONTAINER_NAME = "zkfuse"


class ZKFileSystem(object):
    """
        Mounts an external directory pointed by `remote_path`
        onto `base` (/mnt by default) and passes it to Docker
        to use as a volume.  Uses vol_dict to keep track of
        different volumes.
    """

    def __init__(self, base, zkfuse_opt="-d"):
        self.base = os.path.join(base, 'zkmount')
        os.mkdir(self.base)
        self.zkfuse_options = zkfuse_opt
        self.vol_dict = {}
        self.docker_opt = "run --name {0} --device /dev/fuse --cap-add SYS_ADMIN -d ".format(CONTAINER_NAME)

    def create(self, volname, options):
        """ Creates the directories but does not mount it yet."""
        if 'zookeeper_string' not in options:
            raise NeedOptionsException('zookeeper_string needed')

        zkstring = options['zookeeper_string']
        local_path = os.path.join(self.base, volname)

        log.info('Creating directory ' + local_path)
        os.mkdir(local_path)

        if 'docker_opt' in options:
            # Need to provide "--net=host here if zookeeper is running locally"
            self.docker_opt += options['docker_opt']

        cmdline = self.docker_opt + " -v {hostmount}:/zkmount:shared {dimage} /usr/bin/zkfuse \
                        {zkfuse_opt} -m /zkmount/{volname} -z {zkstring}".format(
            hostmount=self.base,
            zkfuse_opt=self.zkfuse_options,
            zkstring=zkstring,
            dimage=DOCKER_IMAGE,
            volname=volname,
        )

        cmdline = cmdline.split()

        self.vol_dict[volname] = {'Local': local_path, 'cmdline': cmdline, 'mounted': False}

        if 'pull_early' in options:
            cmdstring = "pull " + DOCKER_IMAGE
            cmd = docker[cmdstring.split()]
            cmd()

    def list(self):
        """ Lists the existing volumes being managed."""
        vol_list = []
        for volumes in self.vol_dict:
            vol_list += [volumes]
        return vol_list

    def mount_check(self, volname):
        """Check if the volume is already mounted.
        If mounted, return its path.
        """
        if not self.vol_dict[volname]['mounted']:
            log.error('Volume {0} is not mounted'.format(volname))
            return None
        return self.vol_dict[volname]['Local']

    def path(self, volname):
        """Check if the volume is already mounted.
        If mounted, return its path.
        """
        if not self.mount_check(volname):
            return None

        return self.vol_dict[volname]['Local']

    def remove(self, volname):
        """
            Removes the volume.
            It unmounts the remote if necessary, tolerates
            if already unmounted.
            After which, it removes the mounted directory.
        """
        local_path = self.vol_dict[volname]['Local']
        try:
            self.umount(volname)
        except ProcessExecutionError as e:
            if (e.retcode != 1):
                raise
        log.info('Removing local path ' + local_path)
        if (os.path.exists(local_path)):
            os.rmdir(local_path)
        return True

    def mount(self, volname):
        """ Mount the remote onto local for volname. """
        check = self.mount_check(volname)
        if check:
            return check
        cmdline = self.vol_dict[volname]['cmdline']
        mount_cmd = docker[cmdline]
        mount_cmd()
        self.vol_dict[volname]['mounted'] = True
        return self.vol_dict[volname]['Local']

    def umount(self, volname):
        if not self.mount_check(volname):
            return None
        cmdline = "stop " + CONTAINER_NAME
        umount_cmd = docker[cmdline.split()]
        umount_cmd()
        cmdline = "rm -f " + CONTAINER_NAME
        remove_cmd = docker[cmdline.split()]
        remove_cmd()
        self.vol_dict[volname]['mounted'] = False
        return True

    def cleanup(self):
        """ Unmounts and removes mount paths when shutting down."""
        for volume in self.vol_dict:
            self.remove(volume)
        os.rmdir(self.base)

    def scope(self):
        """ Returns scope of this - global."""
        return "global"
