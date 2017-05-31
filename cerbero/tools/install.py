import os
import re
import tarfile


class InstallError(Exception):
    header = ''
    msg = ''

    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.header + msg)


class PKGConfig(object):

    def __init__(self, fobj):
        self._fobj = fobj
        self._prefix = None
        self._exec_prefix = None
        self._libdir = None
        self.sharedlibdir = None


def commprefix(x, y):
    n = min(len(x), len(y))
    for i in range(n):
        if x[:i + 1] != y[:i + 1]:
            return x[:i]
    else:
        return x[:n]
    return ''


class PCFile(object):

    _PATTERN = re.compile('(?P<name>(\w+))'
  + '=(?P<value>((/\w+|\w\:/|/w\:\\|$\{\w+\})[^\*\?\"<>\|\r\n]+))'
  + '(?P<end>[\r\n])*')

    def __init__(self, file, tar=None):
        self._file = file
        self._dirs = None
        self._lines = []
        self._toformat = {}
        self._vars = {}
        self._prefix = None
        self._ivars = {}  # Intermediate vars

        pos = 0
        for l in self._file.readlines():
            self._lines.append(l)

            m = re.match(PCFile._PATTERN, l)
            if m:
                if m.group('name') == 'prefix':
                    self._prefix = m.group('value')
                self._vars[m.group('name')] = (pos, m.group('value'))
            pos += 1

    def rebuild(self, prefix):

        commprefix = self._parse()
        if commprefix:
            n = commprefix.find('/lib')
            if n:
                commprefix = commprefix[:n]
            for name, value in self._ivars.iteritems():
                self._vars[name] = (self._vars[name][0],
                                  value.replace(commprefix, '${prefix}'))

        self._vars['prefix'] = self._vars['prefix'][0], prefix
        for name, (index, value) in self._vars.iteritems():
            if name == 'prefix':
                value = prefix

            self._lines[index] = '%s=%s\n' % (name, value)
        return "".join(self._lines)

    def _listdirs(self):
        if self._dirs is None:
            self._dirs = set()
            for i in tar.getnames():
                self._dirs.add(os.path.dirname(i).lower())
        return self._dirs

    def _parse(self):
        toformat = {}
        common = None
        for name, (index, value) in self._vars.iteritems():
            if name == 'prefix':
                continue

            if value.startswith(self._prefix):
                self._vars[name] = (index, value.replace(
                    self._prefix, '${prefix}'))
                continue

            self._ivars[name] = value
            if common is None:
                common = value
            else:
                common = commprefix(common, value)
                assert common
        return common

        for name, value in self._ivars.iteritems():
            if value.startswith('$'):
                continue


PKG_PATTERN = re.compile('(?P<name>\w+(-[\w\.]+)*)'
  + '-(?P<platform>(windows|linux))'
  + '-(?P<arch>(x86|x86_64))'
  + '-(?P<version>(\d+(.\d+)*(-\d+)*))'
  + '(-(?P<type>(devel|pdb|test)))?'
  + '(?P<debug>@debug)?'
  + '.tar.bz2')


class Installer(object):

    def __init__(self, prefix):
        self._prefix = prefix

    def _pkginfo(self, tarball):
        pkginfo = re.match(PKG_PATTERN, tarball )
        if not pkginfo:
            raise InstallError('invalied package name :%s' % tarball)

        pkginfo_dict = pkginfo.groupdict()
        if pkginfo_dict['type'] is None:
            pkginfo_dict['type'] = ''
        return pkginfo_dict

    def install(self, path):
        '''
        path - path of the package(tar.bz2)
        '''
        tarball = os.path.basename( path )
        pkginfo = self._pkginfo(tarball)
        if not pkginfo:
            raise InstallError('invalied package name :%s' % tarball)

        #try:
        tar = tarfile.open(path, "r:bz2")
        self._reginfo(tar ,pkginfo)

        self._detar(tar ,pkginfo)

        tar.close()
        #except Exception, e:
        #    raise Exception, e

    def _detar(self, tar,pkginfo):

        if pkginfo['type'] == 'devel':
            for fname in tar.getnames():
                path = os.path.join( self._prefix, fname )
                d = os.path.dirname( path )
                if not os.path.isdir( d):
                    os.makedirs(d)
                
                if fname.endswith('.pc'):                        
                    pc = PCFile( tar.extractfile( fname ) )
                    content = pc.rebuild(self._prefix)
                    f = open( path ,'w')
                    f.write( content )
                    f.close()
                else:
                    tar.extract( fname, self._prefix )
        else:
            tar.extractall( self._prefix)
        
        
    def _reginfo(self, tar,pkginfo):
        if not os.path.isdir(self._prefix):
            os.makedirs( self._prefix )

        infod=os.path.join( self._prefix,'.install',pkginfo['name'],pkginfo['type'])

        if not os.path.isdir( infod ):
            os.makedirs( infod )
        
        path = os.path.join( infod,'desc')
        f = open(path,'w')
        f.write('name:%s\n'%pkginfo['name'])
        f.write('version:%s\n'%pkginfo['version'])
        f.write('arch:%s\n'%pkginfo['arch'])
        if pkginfo == '':
            f.write('type:runtime\n')
        else:
            f.write('type:%s\n'%pkginfo['type'])
        f.close()

        path = os.path.join( infod,'files')
        f = open(path,'w')
        for fname in tar.getnames():
            f.write('%s\n'%fname)
        f.close()
        


def gen_package_desc(name):
    pass

 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()  
    parser.add_argument("package", help="package to be installed",
                    type=str)
    parser.add_argument("--dir", help="directory the package to to be installed",
                    type=str)
    args = parser.parse_args()

    installer = Installer( args.dir )
    installer.install( args.package )
   # 

    #for path in glob.glob(r'D:\tmp\org\*.pc'):
    #    f = open(path)
    #    pc = PCFile(f)
    #    txt = pc.rebuild('c:/@@')
    #    f=open(path.replace('org','rebuild'),'w')
    #    f.write(txt)
    #    f.close
    #    #pc.show()
        
#
#  f = open(r'C:\gstreamer\1.0\x86_64\lib\pkgconfig\zlib.pc')
#  pc = PCFile(f)
#  pc.normlize()
#  pc.show()
#  #inst = Installer('.')
#  
#  #inst.install('base-libs-windows-x86_64-1.12.0-devel.tar.bz2')








#tests=[ 'base-libs-windows-x86_64-1.12.0.tar.bz2',
#        'base-libs-windows-x86_64-1.12.0-devel.tar.bz2',
#        'base-libs-windows-x86-1.12.0-1-devel.tar.bz2' ,
#        'base-libs-windows-x86-1.12.0-1-devel@debug.tar.bz2' ]







