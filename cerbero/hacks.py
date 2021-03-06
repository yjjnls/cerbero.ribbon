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
import sys


### XML Hacks ###

import re
import StringIO
from xml.dom import minidom
from cerbero.utils import etree
oldwrite = etree.ElementTree.write


def pretify(string, pretty_print=True):
    parsed = minidom.parseString(string)
    # See:http://www.hoboes.com/Mimsy/hacks/geektool-taskpaper-and-xml/
    fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')
    return re.sub(fix, '', parsed.toprettyxml())


def write(self, file_or_filename, encoding=None, pretty_print=False):
    if not pretty_print:
        return oldwrite(self, file_or_filename, encoding)
    tmpfile = StringIO.StringIO()
    oldwrite(self, tmpfile, encoding)
    tmpfile.seek(0)
    if hasattr(file_or_filename, "write"):
        out_file = file_or_filename
    else:
        out_file = open(file_or_filename, "wb")
    out_file.write(pretify(tmpfile.read()))
    if not hasattr(file_or_filename, "write"):
        out_file.close()


etree.ElementTree.write = write


### Windows Hacks ###

# On windows, python transforms all enviroment variables to uppercase,
# but we need lowercase ones to override configure options like
# am_cv_python_platform

environclass = os.environ.__class__
import UserDict


class _Environ(environclass):

    def __init__(self, environ):
        UserDict.UserDict.__init__(self)
        self.data = {}
        for k, v in environ.items():
            self.data[k] = v

    def __setitem__(self, key, item):
        os.putenv(key, item)
        self.data[key] = item

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        os.putenv(key, '')
        del self.data[key]

    def pop(self, key, *args):
        os.putenv(key, '')
        return self.data.pop(key, *args)

    def has_key(self, key):
        return key in self.data

    def __contains__(self, key):
        return key in self.data

    def get(self, key, failobj=None):
        return self.data.get(key, failobj)


# we don't want backlashes in paths as it breaks shell commands

oldexpanduser = os.path.expanduser
oldabspath = os.path.abspath
oldrealpath = os.path.realpath


def join(*args):
    return '/'.join(args)


def expanduser(path):
    return oldexpanduser(path).replace('\\', '/')


def abspath(path):
    return oldabspath(path).replace('\\', '/')


def realpath(path):
    return oldrealpath(path).replace('\\', '/')

if sys.platform.startswith('win'):
    os.environ = _Environ(os.environ)
    os.path.join = join
    os.path.expanduser = expanduser
    os.path.abspath = abspath
    os.path.realpath = realpath

import stat
import shutil
from shutil import rmtree as shutil_rmtree
from cerbero.utils.shell import call as shell_call

def rmtree(path, ignore_errors=False, onerror=None):
    '''
    shutil.rmtree often fails with access denied. On Windows this happens when
    a file is readonly. On Linux this can happen when a directory doesn't have
    the appropriate permissions (Ex: chmod 200) and many other cases.
    '''
    def force_removal(func, path, excinfo):
        '''
        This is the only way to ensure that readonly files are deleted by
        rmtree on Windows. See: http://bugs.python.org/issue19643
        '''
        # Due to the way 'onerror' is implemented in shutil.rmtree, errors
        # encountered while listing directories cannot be recovered from. So if
        # a directory cannot be listed, shutil.rmtree assumes that it is empty
        # and it tries to call os.remove() on it which fails. This is just one
        # way in which this can fail, so for robustness we just call 'rm' if we
        # get an OSError while trying to remove a specific path.
        # See: http://bugs.python.org/issue8523
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except OSError:
            shell_call('rm -rf ' + path)
    # We try to not use `rm` because on Windows because it's about 20-30x slower
    if not onerror:
        shutil_rmtree(path, ignore_errors, onerror=force_removal)
    else:
        shutil_rmtree(path, ignore_errors, onerror)

shutil.rmtree = rmtree

### OS X Hacks ###

# use cURL to download instead of wget

if sys.platform.startswith('darwin'):
    import cerbero.utils.shell as cshell
    del cshell.download
    cshell.download = cshell.download_curl

################ CONTINUE HACKS ########################################
from cerbero.utils import messages as m
import shutil


#default mirror
_mirror = os.environ.get('CERBERO_TARBALL_MIRROR')
if _mirror:
    import cerbero.build.source as source
    source.TARBALL_MIRROR = _mirror

if os.path.isfile( os.path.join( os.getcwd(),'bootstrap.py') ):
    sys.path.append( os.getcwd())
    bs = __import__('bootstrap')
    if hasattr( bs, 'pre_bootstrap') or hasattr(bs, 'post_bootstrap'):
        import cerbero.commands.bootstrap
        Bootstrap = cerbero.commands.bootstrap.Bootstrap
        print '=>',Bootstrap
        Bootstrap._run = Bootstrap.run


        def _run(self, config, args):
            print '==========RUN======='
            if hasattr( bs, 'pre_bootstrap'):
                bs.pre_bootstrap( config )
            Bootstrap._run(self,config,args )
            if hasattr( bs, 'post_bootstrap'):
                bs.post_bootstrap( config )
        cerbero.commands.bootstrap.Bootstrap.run = _run

#        print '=>',cerbero.commands.bootstrap.Bootstrap

#
#
#
#
#        def _run(self, config, args):
#
#        bootstrappers = Bootstrapper(config, args.build_tools_only)
#        for bootstrapper in bootstrappers:
#            bootstrapper.start()
#
#    import cerbero.commands.bootstrap.Bootstrap as bootstrap
#    
#
#
#
#_deployer=None
#
#def Deploy():
#    return _deployer
#
#if os.path.isfile( os.path.join( os.getcwd(),'deploy.py') ):
#    sys.path.append( os.getcwd())
#    _deployer = __import__( 'deploy' )
#
#
#
#if _deployer and hasattr(_deployer,'MIRRORS'):
#    import cerbero.utils.shell as cshell
#    cshell._download = cshell.download
#    #del cshell.download
#
#    def _mirror_download(url, destination=None, recursive=False, check_cert=True, overwrite=False):
#        '''
#        Downloads a file with wget, but try mirror first#

#        @param url: url to download
#        @type: str
#        @param destination: destination where the file will be saved
#        @type destination: str
#        '''
#        murl = _deployer.MIRRORS.get( url ,None)
#        if murl is None:
#            part=''
#            for key, value in _deployer.MIRRORS.iteritems():
#                if url.startswith(key):
#                    #find the longest matched
#                    if len(key) > len(part):
#                        part = key
#            if part :
#                murl = url.replace( part , _deployer.MIRRORS[part] )#
#
#        if murl :
#            if murl.startswith('http://') or murl.startswith('https://'):
#                try :
#                    m.message('downloading from mirror %s'%murl)
#                    cshell._download( murl ,destination,recursive,check_cert,overwrite)
#                    return
#                except:
#                    m.warning('download mirror %s failed.'%murl)
#            elif os.path.isfile( murl ) :
#                path = os.path.dirname( murl )
#                if destination:
#                    path = destination
#                shutil.copyfile( murl , path )
#                return
#        cshell._download( url ,destination,recursive,check_cert,overwrite)#
#
#
#    #cshell.download = _mirror_download
