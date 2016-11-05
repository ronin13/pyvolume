# -*- coding: utf-8 -*-

import abc

class FileSystem(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, path):
        pass

    @abc.abstractmethod
    def list(self, path):
        pass

    @abc.abstractmethod
    def remove(self, path):
        pass

    @abc.abstractmethod
    def path(self, volname):
        pass


    @abc.abstractmethod
    def mount(self, path):
        pass

    @abc.abstractmethod
    def umount(self, path):
        pass
