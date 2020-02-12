# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
import json
import sys


def encode(ddict):
    if sys.version_info[0] >= 3:
        return json.dumps(ddict)
    else:
        return json.dumps(ddict).encode('utf-8')


def decode(sstr):
    if sys.version_info[0] >= 3:
        return json.loads(sstr.decode())
    else:
        return json.loads(sstr.decode('utf-8'))
