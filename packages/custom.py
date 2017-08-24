# -*- Mode: Python -*- vi:si:et:sw=4:sts=4:ts=4:syntax=python

from cerbero.packages import package
from cerbero.enums import License

class Ribbon:

    url = ""
    version = '0.3.5'
    vendor = 'Ribbon Project'
    licenses = [License.LGPL]
    org = ''
    requires={
        'gstreamer-1.0':{
            'version':'1.12.2-3'
        }
    }
