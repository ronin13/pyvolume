# -*- coding: utf-8 -*-

from flask import Flask
from flask import json
from flask import request
import os
import tempfile
import os.path
import shutil
import logging

from flask_classy import FlaskView, route
from pyvolume.local import LocalFileSystem

app = Flask(__name__)
PORT = 1331
BASE_PATH = tempfile.mkdtemp()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class VolumeRouter(FlaskView):
    route_base = '/'
    volume_dict = {}

    def __init__(self):
        self.driver = LocalFileSystem(BASE_PATH)

    @route('/')
    def index(self):
        return 'Docker volume driver listening on  ' + str(PORT)


    @route('/VolumeDriver.Create', methods = ['POST'])
    def create_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')

        try:
            self.driver.create(vol_name)
        except Exception as e:
            return json.dumps({"Err": "Failed to create the volume {0}".format(str(e))})

        return json.dumps({"Err": ""})

    @route('/VolumeDriver.Remove', methods = ['POST'])
    def remove_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        try:
            self.driver.remove(vol_name)
        except Exception as e:
            return json.dumps({"Err": "Failed to create the volume {0}".format(str(e))})
        return json.dumps({"Err": ""})

    @route('/VolumeDriver.Mount', methods = ['POST'])
    def mount_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        try:
            mntpoint = self.driver.mount(vol_name)
        except Exception as e:
            return json.dumps({"Mountpoint":"", "Err": "Failed to create the volume {0}".format(str(e))})

        return json.dumps({"Mountpoint": mntpoint, "Err": ""})

    @route('/VolumeDriver.Path', methods = ['POST'])
    def path_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        try:
            mntpoint = self.driver.path(vol_name)
        except Exception as e:
            return json.dumps({"Mountpoint": "", "Err": "Failed to create the volume {0}".format(str(e))})

        return json.dumps({"Mountpoint": mntpoint, "Err": ""})

    @route('/VolumeDriver.UnMount', methods = ['POST'])
    def unmount_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        try:
            self.driver.umount(vol_name)
        except Exception as e:
            return json.dumps({"Err": "Failed to create the volume {0}".format(str(e))})

    @route('/VolumeDriver.Get', methods = ['POST'])
    def get_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        try:
            mntpoint = self.driver.path(vol_name)
        except Exception as e:
            return json.dumps({"Err": "Failed to create the volume {0}".format(str(e))})

        return json.dumps({ "Volume":
                    { "Name" : vol_name,
                    "Mountpount": mntpoint,
                    "Status": {},
                    },
                "Err": "",
               })

    @route('/VolumeDriver.List', methods = ['POST'])
    def list_volume(self):
        rdata = request.get_json(force=True)
        vol_name = rdata['Name'].strip('/')
        vol_list = []
        try:
            vol_list = self.driver.list()
            for volume in vol_list:
                mntpoint = self.driver.path(volume)
                vol_list += [{
                              "Name": volume,
                              "Mountpount": mntpoint,
                            }]

        except Exception as e:
            return json.dumps({"Err": "Failed to create the volume {0}".format(str(e))})

        return json.dumps({ "Volumes": vol_list,
                "Err": "",
               })

    @route('/VolumeDriver.Capabilities', methods = ['POST'])
    def capabilities_volume(self):
        return json.dumps({"Capabilities": {"Scope": "local"}})

VolumeRouter.register(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
