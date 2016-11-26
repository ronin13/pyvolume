# -*- coding: utf-8 -*-
""" Module providing the MountMgr, VolumeManager and Flask methods.
Following Docker Volume endpoints are routed below:

    '/Plugin.Activate'
    '/VolumeDriver.Create'
    '/VolumeDriver.Remove'
    '/VolumeDriver.List'
    '/VolumeDriver.Path'
    '/VolumeDriver.Mount'
    '/VolumeDriver.Unmount'
    '/VolumeDriver.Get'
    '/VolumeDriver.Capabilities'

"""
from __future__ import unicode_literals

import argparse
import logging

from flask import Flask
from flask import jsonify
from flask import request

from pyvolume.local import EphemeralFileSystem
from pyvolume.sshfs import SSHFileSystem
from pyvolume.zkfuse import ZKFileSystem

app = Flask(__name__)
HOST = '0.0.0.0'
PORT = 1331
DRIVER_TYPE = 'sshfs'
DEFAULT_BASE = '/mnt'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MountMgr(object):
    """ MountMgr is a helper class used during mounting/unmounting."""

    def __init__(self, counter, mntpoint):
        self.counter = counter
        self.mntpoint = mntpoint


class VolumeManager(object):
    """ VolumeManager is the class providing pluggable drivers
    for pyvolume, the drivers implementing the methods:

       1. create
       2. list
       3. path
       4. remove
       5. mount
       6. umount
       7. scope
       8. cleanup

    Currently, drivers available are EphemeralFileSystem, SSHFileSystem and Zookeeper FileSystem
    """

    def __init__(self, driver, prefix):
        if (driver == 'ephemeral'):
            self.driver = EphemeralFileSystem(prefix)
        elif (driver == 'sshfs'):
            self.driver = SSHFileSystem(prefix)
        elif (driver == 'zookeeper'):
            self.driver = ZKFileSystem(prefix)

        self.mount_mgr = {}
        self.driver_type = driver

    def cleanup(self):
        """ Cleanup done during shutdown of server."""
        for volume in self.mount_mgr:
            self.mount_mgr[volume].counter = 0
            self.mount_mgr[volume].mntpoint = None

        self.driver.cleanup()


def dispatch(data):
    """ To jsonify the response with correct HTTP status code.

    Status codes:
        200: OK
        400: Error

    Err in JSON is non empty if there is an error.

    """
    if ('Err' in data and data['Err'] != ""):
        code = 400
    else:
        code = 200
    resp = jsonify(data)
    resp.status_code = code
    return resp


@app.route('/Plugin.Activate', methods=['POST'])
def implements():
    """ Routes Docker Volume '/Plugin.Activate'."""
    return dispatch({"Implements": ["VolumeDriver"]})


@app.route('/VolumeDriver.Create', methods=['POST'])
def create_volume():
    """ Routes Docker Volume '/VolumeDriver.Create'."""
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    options = rdata['Opts']

    try:
        volm.driver.create(vol_name, options)
    except Exception as e:
        return dispatch({"Err": "Failed to create the volume {0} : {1}".format(vol_name, str(e))})

    return dispatch({"Err": ""})


@app.route('/')
def index():
    return 'Docker volume driver listening on ' + str(PORT)


@app.route('/VolumeDriver.Remove', methods=['POST'])
def remove_volume():
    """ Routes Docker Volume '/VolumeDriver.Remove'."""
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    try:
        volm.driver.remove(vol_name)
    except Exception as e:
        return dispatch({"Err": "Failed to remove the volume {0}: {1}".format(vol_name, str(e))})
    return dispatch({"Err": ""})


@app.route('/VolumeDriver.Mount', methods=['POST'])
def mount_volume():
    """ Routes Docker Volume '/VolumeDriver.Mount'.

    Handles multiple invocations of mount for same volume.
    """
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    # vol_id = rdata['ID']

    if (vol_name in volm.mount_mgr):
        mntpoint = volm.mount_mgr[vol_name].mntpoint
        volm.mount_mgr[vol_name].counter += 1
        log.info("Volume {0} is mounted {1} times".format(vol_name, volm.mount_mgr[vol_name].counter))
        return dispatch({"Mountpoint": mntpoint, "Err": ""})

    try:
        mntpoint = volm.driver.mount(vol_name)
        volm.mount_mgr[vol_name] = MountMgr(1, mntpoint)
    except Exception as e:
        return dispatch({"Mountpoint": "", "Err": "Failed to mount the volume {0}: {1}".format(vol_name, str(e))})

    return dispatch({"Mountpoint": mntpoint, "Err": ""})


@app.route('/VolumeDriver.Path', methods=['POST'])
def path_volume():
    """ Routes Docker Volume '/VolumeDriver.Path'.
    Returns Err if volume is not mounted.
    """
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    try:
        mntpoint = volm.driver.path(vol_name)
    except Exception as e:
        return dispatch({"Mountpoint": "", "Err": "Failed to obtain path to the volume {0}: {1}".format(vol_name, str(e))})

    if not mntpoint:
        return dispatch({"Mountpoint": "", "Err": "Volume {0} is not mounted".format(vol_name)})

    return dispatch({"Mountpoint": mntpoint, "Err": ""})


@app.route('/VolumeDriver.Unmount', methods=['POST'])
def unmount_volume():
    """ Routes Docker Volume '/VolumeDriver.Unmount'.

        Handles multiple Unmount requests for volume mounted multiple
        times by only unmounting the last time.
    """
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    # vol_id = rdata['ID']

    if (vol_name in volm.mount_mgr):
        # mntpoint = volm.mount_mgr[vol_name].mntpoint
        volm.mount_mgr[vol_name].counter -= 1
        if (volm.mount_mgr[vol_name].counter > 0):
            log.info("Still mounted {0} times to unmount".format(volm.mount_mgr[vol_name].counter))
            return dispatch({"Err": ""})

    try:
        res = volm.driver.umount(vol_name)
        if not res:
            return dispatch({"Err": "Volume {0} may already be unmounted.".format(vol_name)})
        volm.mount_mgr.pop(vol_name)
    except Exception as e:
        return dispatch({"Err": "Failed to umount the volume {0}: {1}".format(vol_name, str(e))})

    return dispatch({"Err": ""})


@app.route('/VolumeDriver.Get', methods=['POST'])
def get_volume():
    """ Routes Docker Volume '/VolumeDriver.Get'."""
    volm = app.config['volmer']
    rdata = request.get_json(force=True)
    vol_name = rdata['Name'].strip('/')
    try:
        mntpoint = volm.driver.path(vol_name)
    except Exception as e:
        return dispatch({"Err": "Failed to get the volume path for {0}: {1}".format(vol_name, str(e))})

    if not mntpoint:
        return dispatch({"Mountpoint": "", "Err": "Volume {0} is not mounted".format(vol_name)})

    return dispatch({"Volume":
                     {"Name": vol_name,
                      "Mountpoint": mntpoint,
                      "Status": {},
                      },
                     "Err": "",
                     })


@app.route('/VolumeDriver.List', methods=['POST'])
def list_volume():
    """ Routes Docker Volume '/VolumeDriver.List'."""
    volm = app.config['volmer']
    mnt_list = []
    try:
        vol_list = volm.driver.list()
        for volume in vol_list:
            mntpoint = volm.driver.path(volume)
            if not mntpoint:
                mntpoint = "<NOT-MOUNTED>"
            mnt_list += [{
                "Name": volume,
                "Mountpoint": mntpoint,
            }]

    except Exception as e:
        return dispatch({"Err": "Failed to list the volumes: {0}".format(str(e))})

    return dispatch({"Volumes": mnt_list,
                     "Err": "",
                     })


@app.route('/VolumeDriver.Capabilities', methods=['POST'])
def capabilities_volume():
    """ Routes Docker Volume '/VolumeDriver.Capabilities'."""
    volm = app.config['volmer']
    scope = volm.driver.scope()
    return dispatch({"Capabilities": {"Scope": scope}})


def shutdown_server():
    """ Utility method for shutting down the server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """ API end point exposed to shutdown the server."""
    shutdown_server()
    return 'Server shutting down...'


parser = argparse.ArgumentParser(description='Arguments to volume router')

parser.add_argument('-t', '--driver', default=DRIVER_TYPE,
                    help='Type of driver to use',
                    choices=['sshfs', 'ephemeral', 'zookeeper']
                    )
parser.add_argument('-H', '--host', default=HOST, help='Host to listen on')
parser.add_argument('-p', '--port', default=PORT, help='Port to listen on')
parser.add_argument('-m', '--base', default=DEFAULT_BASE, help='Base directory to mount over, default is ' + DEFAULT_BASE)


def start():
    global PORT
    global HOST

    args = parser.parse_args()
    PORT = args.port
    HOST = args.host
    volmer = VolumeManager(args.driver, prefix=args.base)
    app.config['volmer'] = volmer

    try:
        app.run(host=args.host, port=args.port)
    finally:
        volmer.cleanup()


if __name__ == '__main__':
    start()
