import os
import re
import tarfile
import urllib2
import shutil
import hashlib
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

def tokenize(line,sep=':'):
    parts = line.split(sep,1)
    if len(parts) == 2:
        return (parts[0],parts[1])
    else:
        return (None,None)

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

def download(url,filename,cb=None):
    if os.path.exists(url):
        shutil.copy( url,filename)
        return 
    f = urllib2.urlopen(url)
    outf = open(filename,'wb')        
    size = 0
    while True:
        data = f.read(1024*32)
        if len(data) == 0:
            break
        outf.write(data)
        size += len(data)
        if cb :
            cb ( size )
def equal( a ,b ):
    return a.lower()==b.lower()

class Fatal(Exception):
    header = ''
    msg = ''

    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.header + msg)


def commprefix(x, y):
    n = min(len(x), len(y))
    for i in range(n):
        if x[:i + 1] != y[:i + 1]:
            return x[:i]
    else:
        return x[:n]
    return ''
class PKGConfig(object):
    # www.freedesktop.org pkg-config file utils

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


class SDKPackage(object):
    

    def __init__(self, prefix, desc):
        self._prefix = prefix
        self._desc = desc

    def setup(self, tarball):
        '''        
        '''
        ext =None
        
        if tarball.endswith('bz2'):
            ext = 'bz2'
        elif tarball.endswith('gz'):
            ext = 'gz'
        else:
            raise Fatal(' not support format %s'%tarball)
        tar = tarfile.open(tarball, "r:"+ext)
        self._reginfo(tar )

        self._detar(tar )

        tar.close()

    def _detar(self, tar):
        if self._desc['Type'] == 'devel':
            for fname in tar.getnames():
                print '~~~~',fname
                path = os.path.join( self._prefix, fname )
                d = os.path.dirname( path )
                if not os.path.isdir( d):
                    os.makedirs(d)
                
                if fname.endswith('.pc'):                        
                    pc = PKGConfig( tar.extractfile( fname ) )
                    content = pc.rebuild(self._prefix)
                    f = open( path ,'w')
                    f.write( content )
                    f.close()
                else:
                    tar.extract( fname, self._prefix )
        else:
            tar.extractall( self._prefix)
        
        
    def _reginfo(self, tar):

        infod = os.path.join(self._prefix, '.install',self._desc['Name'],self._desc['Type'])
        if not os.path.isdir(infod):
            os.makedirs( infod )

        if not os.path.isdir( infod ):
            os.makedirs( infod )
        

        #self._desc.dump( os.path.join(infod, 'desc'))


class DB(object):
    descs=[]


    def __init__(self , prefix, urlbase):
                
        #package path
        path = os.path.join(prefix,  'Packages.tar.gz')
        url  = os.path.join(urlbase, 'Packages.tar.gz')
        md5file =path +'.md5'
        md5url  =url  +'.md5'

        if os.path.exists( path ):
            os.remove( path )
        download( url, path )
        self._load(path)

    def _parse(self, f ):
        item={}
        for line in f.readlines():
            key, value = tokenize(line)
            if key == None:
                continue
            value = value.strip()

            if key == 'Dependencies':
                d=[]
                for sdk in value.split(','):
                    if sdk:
                        name ,version = tokenize(sdk)
                        assert name
                        d.append({'name':name,'version':version})
                value = d

            item[key]=value
        return item

    def _load(self, path):
        tar = tarfile.open(path, "r:gz")
        for fname in tar.getnames():
            item = self._parse( tar.extractfile( fname ) )
            self.descs.append(item)

    def get(self,platform, arch, pkgtype, build):
        for desc in self.descs:
            if equal(desc['Arch'],arch) and \
               equal(desc['Platform'],platform) and \
               equal(desc['Type'],pkgtype) and \
               (equal(desc['Build'],'ReleaseOnly') or  orequal( desc['Build'] , build):
               return desc
        return None

def Setup(prefix , config, arch,platform, build='Release'):
    '''
    config ={
        'repo':'http://XYZ' ,
        'SDK':{
            'gstreamer-1.0':{
                'repo':'/tmp/gstreamer'
                'version':'1.12.2-2'
            }
            'ribbon':{
                'version':'0.2.2'
            }
        }
    }
    '''
    
    default_repo=config.get('repo','')

    for name, value in config['SDK'].iteritems():
        version = value['version']
        repo = os.path.join(default_repo,name) #default
        repo = value.get('repo',repo)
        urlbase = os.path.join(repo,version)
        pkgtypes = value.get('type',['runtime','devel'])
        for pkgtype in pkgtypes: 

            infod = os.path.join(prefix, '.install',name ,pkgtype)
            if not os.path.exists(infod):
                os.makedirs(infod)

            pi = DB(infod ,urlbase)
            
            desc = pi.get(platform,arch,pkgtype,build)
            url = os.path.join( urlbase, desc['Filename'])
            path = os.path.join(infod,desc['Filename'])
            download( url, path)
            md5sum=get_md5(path)
            assert desc['MD5Sum'] == md5sum,'<%s> != <%s>'%(desc['MD5Sum'] , md5sum)

            p = SDKPackage(prefix,desc)
            p.setup( path )




if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()  
    parser.add_argument("package", help="package to be installed",
                    type=str)
    parser.add_argument("--dir", help="directory the package to to be installed",
                    type=str)
#    args = parser.parse_args()
    config ={
        'repo':'http://localhost/wms/sdk/' ,
        'SDK':{
            'gstreamer-1.0':{
                #'repo':'/tmp/gstreamer'
                'version':'1.12.2-1',
                'type':['devel']
            }
            #'ribbon':{
            #    'version':'0.2.2'
            #}
        }
    }

    Setup("./1",config ,'x86_64','Windows')









