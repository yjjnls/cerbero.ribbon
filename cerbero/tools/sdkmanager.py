import os
import re
import tarfile
import urllib2
import shutil








def get_md5(file_path):
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
        

import tarfile
def get_package_info(path):
    info={}
    tar = tarfile.open(path,'r:gz')
    for fname in tar.getnames():
        f = tar.extractfile( fname )
        info[fname]={}
        for line in f.readlines():
            key, value = line.split(':',1)
            info[fname][key]=value
    tar.close()
    return info


class DB(object):

    sdk={
        'sdkname':{
            'package-name':{
                'Package':'',
                'Name':
            }
        }
    }

    def __init__(self):
        '''load SDK infomation accroding path'''
        pass

    def add( self, Packages,version,name):
        info = get_package_info(Packages)
        if not self.sdk.has_key(name):
            self.sdk[name]={}
        self.sdk[name][version]=info


    def _parase(self):
        pass

def Setup(name, sdk ,version,platform ,arch ,debug ,type, prefix,repo):
    '''@description: Install package
    @name  name of the package to be installed
    @prefix   install directory prefix
    @platform Windows,Linux
    @arch     x86 x86_64
    @type     runtime devel
    @debug    True is debug version else release
    @repo     package source url, to be download/copy from there
    @version  SDK version
    @sdk      SDK name
    '''

    #get the Package info files from repo
    url = os.path.join(repo,platform,arch,sdk,version,'Packages.tar.gz')

    sdkd=os.path.join(prefix,'.install',sdk)
    if not os.path.isdir(sdkd):
        os.makedirs(sdkd)
    path=os.path.join(sdkd,'Packages.tar.gz')
    urllib.urlretrieve(url,path)
    urllib.urlretrieve(url+'.md5',path+'.md5')



    #dowload it

def Remove(package, prefix, platform ,arch ,debug ,type):
    # 
    pass

class UrlFile(object):

    def __init__(self,url):
        self.url = url

    def read( self):
        if os.path.isfile( self.url ):
            return open(url,'rb').read()
        else:
            f = urllib2.urlopen(url)
            data = f.read()
            return data

    def copy(self, to)
        if os.path.isfile( self.url ):
            shutil.copy(url,to)
        else:
            f = urllib2.urlopen(url)
            data = f.read()
            with open(to, "wb") as f:
                f.write(data)

            f  = urllib2.urlopen(self.url)
            fout = open(to,'wb')
            
            while True:
                data = f.read(1024*32)
                if len(data) == 0:
                    break
                fout.write(data)
    

class SDKInstaller(object):
    platform=None
    arch=None
    repo=None
    prefix=None
    db=None

    def __init__(self, platform, arch ,repo,prefix):
        self.platform =platform
        self.arch = arch
        self.repo = repo
        self.prefix = prefix

    def setup(self, sdks):
        '''
        pkgs example{
            'gstreamer-1.0':{
                'version':'1.12.2-1',
                'packages':[
                    'base-system-1.0'
                ]
            }
        }

        '''
        self.db = DB()

        for name ,sdk in sdks.iteritems():
            dbpath = os.path.join( self.prefix ,'.install', name,'Package.tar.gz')
            md5path=dbpath+'.md5'
            dburl = os.path.join( self.repo,self.platform,self.arch,name,sdk['version'],'Package.tar.gz')
            md5url=dburl+'.md5'


            md5file=UrlFile(url)

            data = md5file.read()
            md5  = data.split(' ',1)[0]
            
            if os.path.exists(dbpath):
                value = get_md5(dbpath)
                assert md5 == value, 
                'local cached sdk info file is different with remote!\n  local : (%s)\n  remote : %s'%(dbpath,dburl)
            else:
                db =UrlFile(dburl)
                db.copy( dbpath )

            if not os.path.isfile( md5path ):
                md5file.copy(md5path)

            self.db.add( dbpath )



def Deploy():
    deps={
        'gstreamer-1.0':{
            'version':'1.12.2-1',
            'packages':[
                'base-system-1.0'
            ]
        }
    }

    inst=None
#os.path.join(repo,platform,arch,sdk,version,'Packages.tar.gz')

    for name ,sdk in deps.iteritems():
        inst.setup(sdk,name,version)







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







