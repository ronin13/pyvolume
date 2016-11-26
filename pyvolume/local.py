# -*- coding: utf-8 -*-
""" Provides EphemeralFileSystem."""
from __future__ import unicode_literals

import logging
import os
import os.path
import shutil
import tempfile

from plumbum import ProcessExecutionError
from plumbum.cmd import mount
from plumbum.cmd import sudo
from plumbum.cmd import umount

log = logging.getLogger(__name__)

NOT_MOUNTED = '<Not Mounted>'


class EphemeralFileSystem(object):
    """
        Simple docker volume driver which creates a temporary directory
        and then provides it to Docker by mounting it on /mnt.
        Written to test Docker Volume API.
    """

    def __init__(self, remote_prefix):
        self.base = tempfile.mkdtemp()
        log.info("Using {0} as the base".format(self.base))
        self.mount_point = remote_prefix

        self.vol_dict = {}

    def create(self, volname, options):
        path = os.path.join(self.base, volname)
        log.info('Creating directory ' + path)
        os.mkdir(path)

        rpath = os.path.join(self.mount_point, volname)
        os.mkdir(rpath)

        self.vol_dict[volname] = {'Local': path, 'Remote': rpath}

    def list(self):
        return os.listdir(self.base)

    def path(self, volname):
        if self.vol_dict[volname]['Remote'] == NOT_MOUNTED:
            log.error('Volume {0} is not mounted'.format(volname))
            return None

        return self.vol_dict[volname]['Remote']

    def remove(self, volname):
        local_path = self.vol_dict[volname]['Local']
        remote_path = self.vol_dict[volname]['Remote']
        try:
            self.umount(volname)
        except ProcessExecutionError as e:
            if (e.retcode != 1):
                raise
        log.info('Removing remote path ' + remote_path)
        if (os.path.exists(remote_path)):
            os.rmdir(remote_path)

        log.info('Removing local path ' + local_path)
        if (os.path.exists(local_path)):
            shutil.rmtree(local_path)

    def mount(self, volname):
        local_path = self.vol_dict[volname]['Local']
        remote_path = self.vol_dict[volname]['Remote']
        mount_cmd = sudo[mount["-o", "bind,rw", local_path, remote_path]]
        mount_cmd()
        return remote_path

    def umount(self, volname):
        remote_path = self.vol_dict[volname]['Remote']
        umount_cmd = sudo[umount[remote_path]]
        umount_cmd()
        self.vol_dict[volname]['Remote'] = NOT_MOUNTED

    def cleanup(self):
        for volume in self.vol_dict:
            self.remove(volume)
        shutil.rmtree(self.base)

    def scope(self):
        return "local"
