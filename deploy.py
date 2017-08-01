
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

    #
    #
    'http://gstreamer.freedesktop.org/data/cerbero/toolchain/windows' :
        _MIRROR_BASE +  'gstreamer.freedesktop.org/data/cerbero/toolchain/windows',

    'http://ftp.gnome.org/pub/gnome/binaries/win32/' :
        _MIRROR_BASE +  'ftp.gnome.org/pub/gnome/binaries/win32/',

    'https://github.com/Mingyiz/cerbero-archive/raw/master':
        _MIRROR_BASE + 'github.com/cerbero-archive',

    #https://raw.githubusercontent.com/Mingyiz/cerbero-archive/master/MinGW.zip
    'http://www.nasm.us/pub/nasm/releasebuilds/':
        _MIRROR_BASE + 'www.nasm.us/pub/nasm/releasebuilds/',

    'http://www.opengl.org/registry/api/GL/wglext.h':
        _MIRROR_BASE + 'www.opengl.org/registry/api/GL/wglext.h',

    'http://ftp.gnu.org/pub/gnu/' :
        _MIRROR_BASE + 'ftp.gnu.org/pub/gnu/',

    'http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz' :
        _MIRROR_BASE +'www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz',
		
	'http://ftp.acc.umu.se/pub/GNOME/sources/glib/' :
	    _MIRROR_BASE + 'ftp.gnome.org/pub/gnome/sources/glib',
        
    'http://www.openssl.org':
        _MIRROR_BASE + 'www.opengl.org',

}


from cerbero.bootstrap import BootstrapperBase
class FirstBootstrap(BootstrapperBase):
    ''' This planed for user add action at bootstrap step
    '''

    def __init__(self, config):
        BootstrapperBase.__init__(self, config)
             
    def start(self):
        self._load_sources()

    def _load_sources(self):
        if os.path.isdir( 'sources' ):
            return

        url = _MIRROR_BASE + 'gstreamer.freedesktop.org/data/pkg/src/{0}/cerbero-{0}.tar.gz'.format(_VERSION)
        tarball = os.path.basename( url )
        tarball = os.path.join( _CWD , tarball )
        if not os.path.isfile( tarball ):
            shell.download(url, tarball)
        if os.path.isdir('~tmp'):
            shutil.rmtree('~tmp')
        os.makedirs('~tmp')#
        shell.unpack( tarball, './~tmp')
        shutil.move( '~tmp/cerbero-%s/sources'%_VERSION, 'sources' )
        shutil.rmtree('~tmp')#
