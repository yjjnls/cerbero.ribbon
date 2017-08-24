
from cerbero.bootstrap import BootstrapperBase
from cerbero.packages  import tarball
import os
import sys


def pre_bootstrap( config):
    sys.path.append('packages')
    import custom
    sdk = getattr(custom,'Ribbon')
    print os.environ['CERBERO_SDK_REPO'],'<---'

    tarball.Setup( config.prefix,
    {'repo':os.environ['CERBERO_SDK_REPO'] ,'SDK': sdk.requires} ,
    config.target_arch,
    config.target_platform)

def post_bootstrap( config):
    pass
