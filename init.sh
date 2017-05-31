
function fail_exit(){
    if [ $1 -ne 0 ] ; then
	    echo -e "\033[31m $2 \033[0m" 
		exit /b 1
	fi
}




if [ $MSYSTEM == msys ] ; then 

_PYTHON_HINT='Please install 64bit python 2.7,you can download from
  https://www.python.org/ftp/python/2.7.13/python-2.7.13.amd64.msi'
  
_GIT_HINT='Please Install 64bit git, you can get it from
  https://github.com/git-for-windows/git/releases/download/v2.13.0.windows.1/Git-2.13.0-64-bit.exe'

_CMAKE_HINT='Please Install 64bit cmake, you can get it from
  https://cmake.org/files/v3.8/cmake-3.8.1-win64-x64.msi'
  
	MSYS2_PATH="/usr/local/bin:/usr/bin:/bin"
	_SYSTEMROOT="$(PATH=${MSYS2_PATH} cygpath -Wu)"
	_SYSTEM_PATH="${_SYSTEMROOT}/System32:${_SYSTEMROOT}"
	_SYSTEM_PATH="${_SYSTEM_PATH}:${SYSTEMROOT}/System32/Wbem"
	_SYSTEM_PATH="${_SYSTEM_PATH}:${SYSTEMROOT}/System32/WindowsPowerShell/v1.0/"

	PATH="${MSYS2_PATH}:/opt/bin:${_SYSTEM_PATH}"
	
	#Python check
	KEY='HKLM\SOFTWARE\Python\PythonCore\2.7\InstallPath'
	entry=$(reg query ${KEY} //ve | awk '{ if($2=="REG_SZ") print $0}')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}):$PATH
	python_version=$(python --version)
	fail_exit $? "$_PYTHON_HINT"

	KEY='HKLM\SOFTWARE\GitForWindows'
	entry=$(reg query ${KEY} //v InstallPath | awk '{ if($2=="REG_SZ") print $0 }')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}/cmd):$PATH
	git_version=$(git --version)
	fail_exit $? "${_GIT_HINT}"
	
	KEY='HKLM\SOFTWARE\Kitware\CMake'
	entry=$(reg query ${KEY} //v InstallDir | awk '{ if($2=="REG_SZ") print $0 }')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}/bin):$PATH
	
	cmake_version=$(cmake --version)
	fail_exit $? "${_CMAKE_HINT}"	
	
	echo $git_version
	echo $cmake_version
	echo $python_version
	echo "@@"
fi


#KEY='HKLM\SOFTWARE\Python\PythonCore\2.7\InstallPath'
#d=$(reg query ${KEY} //ve | awk '{ if($2=="REG_SZ") print $3}')
#PATH=$(cygpath -u ${d}):$PATH
#python --version
#if [ $? -ne 0 ] ; then
#   echo 'Can not find python, please install the 64bit python 2.7'
#fi
#
#read 