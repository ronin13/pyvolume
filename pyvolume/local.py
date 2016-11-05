import abc
from pyvolume.fs import Filesystem
import os
import tempfile
import os.path
import shutil
import plumbum
from plumbum.cmd import mount, umount

class LocalFileSystem(Filesystem):

    def __init__(self, base):
        self.base = base
        self.mount_point = "/mnt"
        self.mount_options = " -o bind,rw "

        self.vol_dict = {}

    def create(self, volname):
        path = os.path.normpath(self.base, volname)
        log.info('Creating directory ' + path)
        os.mkdir(path)

        rpath = os.path.normpath(self.mount_point, volname)
        os.mkdir(rpath)

        self.vol_dict[volname] = {'Local': path, 'Remote': rpath}

    def list(self):
        return os.listdir(self.base)

    def path(self, volname):
        return self.vol_dict[volname]['Remote']

    def remove(self, volname):
        local_path = self.vol_dict[volname]['Local']
        remote_path = self.vol_dict[volname]['Remote']
        self.umount(remote_path)
        log.info('Removing path ' + local_path)
        # shutil.rmtree(volname)

    def mount(self, volname):
        local_path = self.vol_dict[volname]['Local']
        remote_path = self.vol_dict[volname]['Remote']
        mount([self.mount_options, local_path, remote_path])
        return remote_path

    def umount(self, volname):
        remote_path = self.vol_dict[volname]['Remote']
        umount(remote_path)


