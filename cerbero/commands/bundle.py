

from cerbero.commands import Command, register_command
from cerbero.build.cookbook import CookBook
from cerbero.build.source import SourceType
from cerbero.packages.packagesstore import PackagesStore
from cerbero.bootstrap.build_tools import BuildTools
from cerbero.utils import _, N_, ArgparseArgument, remove_list_duplicates
from cerbero.utils import messages as m
from setuptools.sandbox import run_setup
from cerbero.packages import PackageType
import os


import hashlib
import os
import datetime
import json


def get_file_md5(filename):
    if not os.path.isfile(filename):
        return
    md5hash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        data = f.read(8096)
        if not data :
            break
        md5hash.update(data)
    f.close()
    return md5hash.hexdigest()


class Bundle(Command):
    doc = N_('Bundle package ')
    name = 'bundle'

    def __init__(self, args=[]):
        args = [
            ArgparseArgument('packages', nargs='+', 
                             help=_('packages to bundle')),
            ArgparseArgument('--dir', default='.',
                             help=_('directory where the packages stored in it')),
        ]
        Command.__init__(self, args)

    def _get_name(self, name, package_type,config, package, ext='tar.bz2'):
        return "%s-%s-%s-%s%s.%s" % (name,
            config.target_platform, config.target_arch,
            package.version, package_type, ext)

    def run(self, config, args):
        packages = []
        recipes = []
        bundle_recipes = []
        bundle_dirs = []
        setup_args = ['sdist']
        bundle={}

        if not config.uninstalled:
            m.error("Can only be run on cerbero-uninstalled")

        store = PackagesStore(config)
        cookbook = CookBook(config)

        packages = list(args.packages)
        directory=args.dir
        self.store = PackagesStore(config)
        for name in packages:            
            p = self.store.get_package(name)
            for ptype in [ PackageType.RUNTIME ,PackageType.DEVEL ]:

                tarball = self._get_name( name , ptype,config, p)
                path = os.path.join( directory, tarball )
                print path
                if os.path.isfile( path ):
                    
                    desc={"name":name,
                          "version":p.version,
                          "tarball":tarball,
                          "md5": get_file_md5(path),                          
                          "deps":[]
                          }
                    for pkg in p.deps:
                        deppkg = self.store.get_package(pkg)
                        desc["deps"].append( { "name":pkg,
                            "version":deppkg.version
                        })

                    f = open( path.replace("tar.bz2","json"),"w")
                    data = json.dumps(desc, indent=2)
                    f.write( data )
                    f.close()


register_command(Bundle)
