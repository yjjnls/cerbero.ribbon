# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os

from cerbero.config import Platform
from cerbero.commands import Command, register_command
from cerbero.errors import UsageError
from cerbero.build.cookbook import CookBook
from cerbero.utils import _, N_, ArgparseArgument
from cerbero.utils import messages as m

from cerbero.packages.packagesstore import PackagesStore
from cerbero.packages import PackageType
import os


import hashlib
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

class GenPackageProfile(Command):
    doc = N_('Generate Package tarball description file')
    name = 'genpackageprofile'

    def __init__(self):
        Command.__init__(self,
            [ArgparseArgument('-o', '--output_dir', default=None,
                help=_('output directory where description files will be saved(it also the tarball saved place)')),
            ArgparseArgument('packages', nargs='+', 
                help=_('packages to be generated description file')),
            ])

    def run(self, config, args):

        cookbook = CookBook(config)

        packages = list(args.packages)
        directory=args.output_dir
        self.store = PackagesStore(config)
        for name in packages:            
            package = self.store.get_package(name)
            version = package.version
            platform = config.target_platform
            arch = config.target_arch

            for ptype in [ PackageType.RUNTIME ,PackageType.DEVEL ]:

                tarname = "%s-%s-%s-%s%s" % (name,platform, arch, version, ptype )
                path = os.path.join( directory, tarname+'.tar.bz2' )

                if not os.path.isfile( path ):
                    continue
                    
                profile={"name":name,
                        "version":package.version,
                        "tarball":os.path.basename(path),
                        "md5": get_file_md5(path),                          
                        "deps":[]
                        }
                for dep in package.deps:
                    pkg = self.store.get_package(dep)
                    profile["deps"].append( { 
                        "name":dep,
                        "version":pkg.version
                    })

                f = open( os.path.join( directory,tarname+'.json'),"w")
                data = json.dumps(profile, indent=2)
                f.write( data )
                f.close()


register_command(GenPackageProfile)
