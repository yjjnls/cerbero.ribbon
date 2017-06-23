import os
import json

from cerbero.config import Config, Platform, DistroVersion
from cerbero.bootstrap import BootstrapperBase
from cerbero.build.oven import Oven
from cerbero.build.cookbook import CookBook
from cerbero.utils import _
from cerbero.utils import shell
from cerbero.errors import FatalError, ConfigurationError
from cerbero.tools import install


class Project(BootstrapperBase):
    def __init__(self, config):
        BootstrapperBase.__init__(self, config)
        self.prj_config = {}
        path = os.path.join(os.getcwd(), 'cerbero.json')
        if os.path.isfile(path):
            self.prj_config = json.load(open(path))

    def start(self):
        print 'Project bootstrap-----------'
        self._install_sdk()
        print '------END OF Project--------'

    def _install_sdk(self):
        if not self.prj_config:
            return
        SDKs = self.prj_config.get('SDK', {})
        repo_server = self.prj_config['repo']

        for name, pkg in SDKs.iteritems():
            types = pkg.get('type', ['runtime', 'devel'])
            platform = self.config.target_platform
            arch = self.config.target_arch
            version = pkg['version']

            for t in types:
                type_suffix = {'runtime': '', 'devel': '-devel'}[t]
                if self.config.build_type == 'Debug':
                    tarball = '%s-Debug-%s-%s-%s%s.tar.bz2' % (
                        name, platform, arch, version, type_suffix)
                    tarball_release = '%s-%s-%s-%s%s.tar.bz2' % (
                        name, platform, arch, version, type_suffix)
                else:
                    tarball = '%s-%s-%s-%s%s.tar.bz2' % (name, platform, arch,
                                                         version, type_suffix)
                url = os.path.join(repo_server, platform, arch, tarball)

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
                installer = install.Installer(self.config.install_dir)
                installer.install(destination)
