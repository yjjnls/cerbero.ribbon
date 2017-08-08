
import os
import sys
import shutil
from cerbero.utils  import shell

_CWD  = os.path.abspath( os.getcwd() )

_BASE='http://vss.kedacom.com/WMS'
_SDK='%s/SDK'%_BASE



def version(klass):
    sys.path.append('packages')
    import custom
    sdk = getattr(custom,klass)
    return sdk.version


MIRRORS={

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
        sys.path.append('packages')
        import custom
        sdk = getattr(custom,'Ribbon')
        config ={
            'repo':_SDK ,
            'SDK': sdk.requires
            
        }
        print self.config.prefix,'<--'
        tarball.Setup( self.config.prefix,config ,self.config.target_arch,self.config.target_platform)

