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
import tarfile

import cerbero.utils.messages as m
from cerbero.utils import _
from cerbero.errors import UsageError, EmptyPackageError
from cerbero.packages import PackagerBase, PackageType
from cerbero.packages.packagesstore import PackagesStore
from cerbero.packages.package       import SDKPackage
import hashlib
from cerbero.utils import shell

DESC_TPL = '''
Name:          %(Name)s
Version:       %(Version)s
Platform:      %(Platform)s
Arch:          %(Arch)s
Type:          %(Type)s
Build:         %(Build)s
Homepage:      %(Homepage)s
Dependencies:  %(Dependencies)s
Licences:      %(Licences)s
MD5Sum:        %(MD5Sum)s
Description:   %(Description)s
'''

class DistTarball(PackagerBase):
    ''' Creates a distribution tarball '''

    def __init__(self, config, package, store):
        PackagerBase.__init__(self, config, package, store)
        self.package = package
        self.prefix = config.prefix
        self.package_prefix = ''
        if self.config.packages_prefix is not None:
            self.package_prefix = '%s-' % self.config.packages_prefix

    def pack(self, output_dir, devel=True, force=False, keep_temp=False,
             split=True, package_prefix=''):
        try:
            dist_files = self.files_list(PackageType.RUNTIME, force)
        except EmptyPackageError:
            m.warning(_("The runtime package is empty"))
            dist_files = []

        if devel:
            try:
                devel_files = self.files_list(PackageType.DEVEL, force)
            except EmptyPackageError:
                m.warning(_("The development package is empty"))
                devel_files = []
        else:
            devel_files = []

        if not split:
            dist_files += devel_files

        if not dist_files and not devel_files:
            raise EmptyPackageError(self.package.name)

        filenames = []
        if dist_files:
            runtime = self._create_tarball(output_dir, PackageType.RUNTIME,
                                           dist_files, force, package_prefix, algorithm)
            filenames.append(runtime)

        if split and devel and len(devel_files) != 0:
            devel = self._create_tarball(output_dir, PackageType.DEVEL,
                                         devel_files, force, package_prefix, algorithm )
            filenames.append(devel)
        return filenames

    def _get_name(self, package_type, ext='tar.bz2'):
        return "%s%s-%s-%s-%s%s.%s" % (self.package_prefix, self.package.name,
                self.config.target_platform, self.config.target_arch,
                self.package.version, package_type, ext)

    def _create_tarball(self, output_dir, package_type, files, force,
                        package_prefix, algorithm):
        filename = os.path.join(output_dir, self._get_name(package_type,'tar.'+algorithm))
        if os.path.exists(filename):
            if force:
                os.remove(filename)
            else:
                raise UsageError("File %s already exists" % filename)

        tar = tarfile.open(filename, "w:"+algorithm)

        for f in files:
            filepath = os.path.join(self.prefix, f)
            tar.add(filepath, os.path.join(package_prefix, f))
        tar.close()

        self._create_tarball_desc(package_type,filename)

        return filename

    def _create_tarball_desc(self, package_type, filename):
        ''' we only generate description for SDK package
        '''
        if not isinstance(self.package, SDKPackage):
            #skip for NONE SDK packag
            return 

        store = PackagesStore(self.config)
        p = self.package
        licenses = [p.license]

        basename = os.path.basename(filename)
        outdir = os.path.dirname(filename)

        build = 'ReleaseOnly'
        if hasattr(self.config,'build_type'):
            build=self.config.build_type

        d = {
             'Name': p.name, 'version': p.version, 'url': p.url,
             'Licenses': ' and '.join([l.acronym for l in licenses]),
             'Description': p.shortdesc,
             'Filename':basename,
             'MD5Sum':self._get_md5(filename),
             'Type':{PackageType.DEVEL:'devel',PackageType.RUNTIME:'runtime'}[package_type],
             'Build':build,
             'Platform':self.config.target_platform,
             'Arch':self.config.target_arch,
             'Dependencies': ''}
             
        f =open(basename+'.desc','w')
        
        f.write(DESC_TPL % d)
        f.close()


    def _get_md5(self,file_path):
        f = open(file_path,'rb')  
        md5_obj = hashlib.md5()
        while True:
            d = f.read(8096)
            if not d:
                break
            md5_obj.update(d)
        hash_code = md5_obj.hexdigest()
        f.close()
        md5 = str(hash_code).lower()
        return md5


class Packager(object):

    def __new__(klass, config, package, store):
        return DistTarball(config, package, store)



def register():
    from cerbero.packages.packager import register_packager
    from cerbero.config import Distro
    register_packager(Distro.NONE, Packager)
    register_packager(Distro.GENTOO, Packager)
