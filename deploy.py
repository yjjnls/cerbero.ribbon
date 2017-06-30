#
# 
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

import os
import sys
import shutil
from cerbero.utils  import shell
_VERSION='1.12.0' #cerbero version
_CWD  = os.path.abspath( os.getcwd() )
_REPO_URL='http://localhost/mms/repo/'
_MIRROR_BASE='http://localhost/mms/repo/mirror/'

def prepare():
    ''' This will be called almose before any cerbero action
        (actually after hacks)
        normally you will load sources, recpes or packages according your needs
    '''
    pass

from cerbero.bootstrap import BootstrapperBase
class Bootstrap(BootstrapperBase):
    ''' This planed for user add action at bootstrap step
    '''
    _server = _REPO_URL +'sdk/'
    _SDKs ={ 'gstreamer-1.0':{'version':'1.12.0-1'}
    }
    def __init__(self, config):
        BootstrapperBase.__init__(self, config)
             
    def start(self):
        self._install_sdk()

    def _install_sdk(self):

        for name, pkg in self._SDKs.iteritems():
            types = pkg.get('type', ['runtime', 'devel'])
            platform = self.config.target_platform
            arch = self.config.target_arch
            version = self._SDKs[name]['version']

            for t in types:
                type_suffix = {'runtime': '', 'devel': '-devel'}[t]
                tarball = '%s-%s-%s-%s%s.tar.bz2' % (name, platform, arch,
                             version, type_suffix)

                if self.config.build_type == 'Debug' and  name not in ['gstreamer-1.0'] :
                    tarball = '%s-Debug-%s-%s-%s%s.tar.bz2' % (
                        name, platform, arch, version, type_suffix)

                url = os.path.join( self._server , platform, arch, tarball)

                destination = os.path.join(self.config.install_dir, tarball)
                print '\n%s\n' % url
                rc = shell.download(url, destination)
                if rc == -1 and 'tarball_release' in locals().keys():
                    url = os.path.join(repo_server, platform, arch,
                                       tarball_release)
                    destination = os.path.join(self.config.install_dir,
                                               tarball_release)
                    rc = shell.download(url, destination)
                if rc == -1:
                    continue
                from cerbero.tools.sdkmanager import Installer
                installer = Installer(self.config.install_dir)
                installer.install(destination)