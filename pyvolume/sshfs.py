# -*- coding: utf-8 -*-
""" Module providing SSHFileSystem implementation."""
from __future__ import unicode_literals

import logging
import os
import os.path

from plumbum import ProcessExecutionError
from plumbum.cmd import sshfs
from plumbum.cmd import sudo
from plumbum.cmd import umount

from pyvolume.exceptions import NeedOptionsException

log = logging.getLogger(__name__)


class SSHFileSystem(object):
    """
        Mounts an external directory pointed by `remote_path`
        onto `base` (/mnt by default) and passes it to Docker
        to use as a volume.  Uses vol_dict to keep track of
        different volumes.
    """

    def __init__(self, base):
        self.base = base
        self.sshfs_options = ["-o", "reconnect,cache_timeout=60,allow_other,uid=1000,gid=1000,intr"]
        self.vol_dict = {}

    def create(self, volname, options):
        """ Creates the directories but does not mount it yet."""
        if 'remote_path' not in options:
            raise NeedOptionsException('remote_path is a required option for sshfs')

        remote_path = options['remote_path']
        local_path = os.path.join(self.base, volname)

        log.info('Creating directory ' + local_path)
        os.mkdir(local_path)
        cmdline = []

        if 'ssh_config' in options:
            cmdline += ["-F", options['ssh_config']]

        if 'sshfs_options' in options:
            sshfs_options = [options['sshfs_options']]
        else:
            sshfs_options = self.sshfs_options

        cmdline += [remote_path]
        cmdline += [local_path]
        cmdline += sshfs_options
        self.vol_dict[volname] = {'Local': local_path, 'Remote': remote_path, 'cmdline': cmdline, 'mounted': False}

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
        mount_cmd = sshfs[cmdline]
        mount_cmd()
        self.vol_dict[volname]['mounted'] = True
        return self.vol_dict[volname]['Local']

    def umount(self, volname):
        if not self.mount_check(volname):
            return None
        local_path = self.vol_dict[volname]['Local']
        umount_cmd = sudo[umount[local_path]]
        umount_cmd()
        self.vol_dict[volname]['mounted'] = False
        return True

    def cleanup(self):
        """ Unmounts and removes mount paths when shutting down."""
        for volume in self.vol_dict:
            self.remove(volume)

    def scope(self):
        """ Returns scope of this - global."""
        return "global"
