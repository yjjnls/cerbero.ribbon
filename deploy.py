
import os
import sys
import shutil
from cerbero.utils  import shell
_VERSION='1.12.2' #cerbero version
_CWD  = os.path.abspath( os.getcwd() )
_MIRROR_BASE='http://vss.kedacom.com/WMS/Mirrors/'





#shell.download('http://vss.kedacom.com/rd/sca/FOSS/Theron-6.00.02.zip','./theron.zip')

'http://gstreamer.freedesktop.org/data/cerbero/toolchain/windows'
"mingw-%s-gcc-%s-%s-%s.tar.xz"



MIRRORS={

        
    'http://www.openssl.org':
        _MIRROR_BASE + 'www.opengl.org',

}


from cerbero.bootstrap import BootstrapperBase
from cerbero.packages  import tarball

class FirstBootstrap(BootstrapperBase):
    ''' This planed for user add action at bootstrap step
    '''

    def __init__(self, config):
        BootstrapperBase.__init__(self, config)
             
    def start(self):
        self._insall_sdk()

    def _insall_sdk(self):
        config ={
            'repo':'D:/tmp/SDK' ,
            'SDK':{
                'gstreamer-1.0':{
                    'version':'1.12.2-1',
                }
            }
        }
        tarball.Setup( self.config.prefix,config ,self.config.target_arch,self.config.target_platform)

