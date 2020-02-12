#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_pyvolume_sshfs
----------------------------------

Tests for `pyvolume` module for sshfs implementation.
"""
from __future__ import absolute_import
import os
import unittest

import pytest
from mock import patch

import pyvolume.manager as manager
from pyvolume.json_func import decode
from pyvolume.json_func import encode

# List of endpoints to be tested.
E_IMPLEMENTS = '/Plugin.Activate'
E_CREATE = '/VolumeDriver.Create'
E_REMOTE = '/VolumeDriver.Remove'
E_LIST = '/VolumeDriver.List'
E_PATH = '/VolumeDriver.Path'
E_MOUNT = '/VolumeDriver.Mount'
E_UNMOUNT = '/VolumeDriver.Unmount'
E_GET = '/VolumeDriver.Get'
E_CAPAB = '/VolumeDriver.Capabilities'
E_GET = '/'
E_SHUTDOWN = '/shutdown'

manager.HOST = '0.0.0.0'
manager.PORT = '13313'
# TEST_URL = 'http://{0}:{1}'.format(TEST_HOST, TEST_PORT)

volmer = manager.VolumeManager('sshfs', '/mnt')


class ManagerTestCase(unittest.TestCase):

    def setUp(self):
        manager.app.config['TESTING'] = True
        manager.app.config['volmer'] = volmer
        self.app = manager.app.test_client()

    def test_get(self):
        rv = self.app.get(E_GET)
        assert b'Docker volume driver listening on ' + str.encode(manager.PORT) in rv.data
        self.assertEqual(rv.status_code, 200)

    def test_implements(self):
        rv = self.app.post(E_IMPLEMENTS)
        self.assertEqual({"Implements": ["VolumeDriver"]}, decode(rv.data))
        self.assertEqual(rv.status_code, 200)

    def test_create(self):
        with patch.object(os, 'mkdir', return_value=None):
            rv = self.app.post(E_CREATE, data=encode({
                "Name": "TESTVOL",
                "Opts": {
                    "remote_path": "server:/home/user",
                },
            }), content_type='application/json')
            self.assertEqual({"Err": ""}, decode(rv.data))
            self.assertEqual(rv.status_code, 200)

            rv = self.app.post(E_CREATE, data=encode({
                "Name": "TESTVOL",
                "Opts": {},
            }), content_type='application/json')
            self.assertEqual({"Err": "Failed to create the volume TESTVOL : remote_path is a required option for sshfs"},
                             decode(rv.data))
            self.assertEqual(rv.status_code, 400)

    def test_shutdown(self):
        with pytest.raises(RuntimeError):
            self.app.post(E_SHUTDOWN)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
