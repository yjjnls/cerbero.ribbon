import os
import os
import sys
import subprocess
import _winreg as winreg

from cerbero.config import Architecture

class ActivePerl( object):
    
    _PROFILE={}

    def __init__(self, version=None):
        self._version = version

    def profile( self ):
        p = ActivePerl._PROFILE.get(self._version,{})
        if not p:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg,r'SOFTWARE\ActiveState\ActivePerl')
            version,typ = winreg.QueryValueEx(key,"CurrentVersion")

            key = winreg.OpenKey(reg,r'SOFTWARE\ActiveState\ActivePerl\%s'%version)
            d,typ = winreg.QueryValueEx(key,"")
            #help,typ = winreg.QueryValueEx(key,"Help")
            p ={'dir':d,'version':version}
            ActivePerl._PROFILE[version]=p
        return p

    def path( self , name='perl'):
        p = self.profile()
        if name == 'perl':
            return os.path.join( p['dir'],'bin/perl')
        return None

_comspec =os.environ.get('COMSPEC') 
_SystemRoot =os.environ.get('SYSTEMROOT')
_SysPathDict={'SystemRoot': _SystemRoot,
        'System32':"%s\\System32"%_SystemRoot,
        'Wbem':"%s\\System32\\Wbem"%_SystemRoot,
        'PowerShell':"%s\\System32\\WindowsPowerShell\\v1.0\\"%_SystemRoot
        }
_SysPath='%(SystemRoot)s;%(System32)s;%(Wbem)s;%(PowerShell)s'%_SysPathDict

class VisualStudio(object):
    #code
    _PROFILE={}


    _DEFAULT_ENV={'INCLUDE':'','LIB':'','LIBPATH':'',
    'VSINSTALLDIR':'','WINDOWSSDKDIR':'',
    'FrameworkDir':'','VCINSTALLDIR':'','DevEnvDir':'',
    'FrameworkDIR64':'',
    'WindowsSDK_ExecutablePath_x64':'',
    'WindowsSDK_ExecutablePath_x86':'',
    'VisualStudioVersion':'' ,
    'VisualStudioPath':''}

    _ENVIRN={}
    _PATH=None


    #_version_map={ '2013':'12.0', '2015':'14.0','2017':'15.0' }
    #_arch_map={ Architecture.X86:'x86',Architecture.X86_64:'amd64' }
    
    def __init__(self, arch ,year = '2015'):
        self._version = { '2013':'12.0', '2015':'14.0','2017':'15.0' }[year]
        self._arch = arch


    def environ(self):
        _CLEAR_COMPILE_VAR_NAME=['CFLAGS', 'CXXFLAGS', 'OBJCFLAGS', 'LDFLAGS',
        'CC', 'CXX', 'LD', 'CPP', 'CXXCPP', 
        'RANLIB','AR','AS','NM', 'WINDRES','RC','DLLTOOL','LD_LIBRARY_PATH']
        env = self._probe()
        for i in _CLEAR_COMPILE_VAR_NAME:
            env[i]=None
        return env
    





    def _probe( self ):
        
        arch={ Architecture.X86:'x86',Architecture.X86_64:'amd64' }[self._arch]
        env=VisualStudio._DEFAULT_ENV
        
        #find vcvarsall.bat
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg,
                r'SOFTWARE\Wow6432Node\Microsoft\VisualStudio\%s\Setup\VC'%self._version)        
        path = winreg.QueryValueEx(key, 'ProductDir')[0]
        vcvarsall='%s\\vcvarsall.bat'%path
        assert os.path.isfile( vcvarsall )
        
        cmd =[ _comspec,'/c', 'PATH=%s'%_SysPath,'&&',
              vcvarsall, arch ,'&&' ,'set']
        
        out =subprocess.check_output( cmd )
        for line in out.splitlines():
            i = line.find('=')
            if i == -1:
                continue
            
            key,value = line[0:i].upper(), line[i+1:]
            
            if key == 'PATH':
                for p in value.split(';'):
                    if p in _SysPathDict.values():
                        continue

                    if env['VisualStudioPath']:
                        env['VisualStudioPath'] +=';'
                    env['VisualStudioPath'] += p
                    
            for k,v in env.iteritems():
                if k.upper() == key:
                    env[k]=value
                    break
        return env

#_COMPILE_VARS={}
#_COMPILE_VAR_NAME=['CFLAGS', 'CXXFLAGS', 'OBJCFLAGS', 'LDFLAGS'
#'CC', 'CXX', 'LD', 'CPP', 'CXXCPP', 
#'RANLIB','AR','AS','NM', 'WINDRES','RC','DLLTOOL','LD_LIBRARY_PATH']#

#_CV_RECOVER={}#

#def clear_cv( recover=None):
#    '''
#    clear the compile releate enviroment vars
#    if you plan to recover it set recover param
#    '''
#    if recover :
#        _CV_RECOVER[recover] = {}
#    for i in _COMPILE_VAR_NAME:
#        if recover:
#            _CV_RECOVER[recover][i]=os.environ[i]
#        os.environ[i]=''#

#def recover_cv( recover ):
#    r = _CV_RECOVER.get( recover,{})
#    if not r:
#        return
#    for k ,v in r.iteritems():
        os.environ[i] = v