
function fail_exit(){
    if [ $1 -ne 0 ] ; then
	    echo -e "\n\n\r\033[1;34m\t$2 \033[0m\n\n"		
		n=9
		while [ $n -gt 0 ];do
			echo -e "\rexit after $n seconds.\c"
			sleep 1
			let n--
        done
	    exit /b 1
	fi
}


function msys2_load_path(){

_PYTHON_HINT='Please install 64bit Python 2.7,you can download from
  https://nodejs.org/dist/v6.11.1/node-v6.11.1-x64.msi'

_PYTHON_HINT='Please install 64bit Node.js ,you can download from
  https://www.python.org/ftp/python/2.7.13/python-2.7.13.amd64.msi'
  
_GIT_HINT='Please Install 64bit git, you can get it from
  https://github.com/git-for-windows/git/releases/download/v2.13.0.windows.1/Git-2.13.0-64-bit.exe'

_CMAKE_HINT='Please Install 64bit cmake, you can get it from
  https://cmake.org/files/v3.8/cmake-3.8.1-win64-x64.msi'
  
	MSYS2_PATH="/usr/local/bin:/usr/bin:/bin"
	_SYSTEMROOT="$(PATH=${MSYS2_PATH} cygpath -Wu)"	
	_SYSTEM_PATH="${_SYSTEMROOT}/System32:${_SYSTEMROOT}"
	_SYSTEM_PATH="${_SYSTEM_PATH}:${_SYSTEMROOT}/System32/Wbem"
	_SYSTEM_PATH="${_SYSTEM_PATH}:${_SYSTEMROOT}/System32/WindowsPowerShell/v1.0/"

	PATH="${MSYS2_PATH}:/opt/bin:${_SYSTEM_PATH}"
	
	#reconfig /etc/pacman.conf
	if [ ! -f /etc/pacman.conf.wms-build-backup ]; then
	   mv -f /etc/pacman.conf /etc/pacman.conf.wms-build-backup
	   echo -e '[options]
Architecture = auto
CheckSpace
SigLevel    = Required DatabaseOptional
LocalFileSigLevel = Optional

[msys]
Server = http://vss.kedacom.com/wms/mirrors/msys2/msys/$arch

#Server = http://mirrors.ustc.edu.cn/msys2/msys/$arch
#Server = https://mirrors.tuna.tsinghua.edu.cn/msys2/msys/$arch
' > /etc/pacman.conf
	   pacman -Syy
	   fail_exit $? "Update pacman database failed, please fix."
	   
	fi
	#Python check
	KEY='HKLM\SOFTWARE\Python\PythonCore\2.7\InstallPath'
	entry=$(reg query ${KEY} //ve | awk '{ if($2=="REG_SZ") print $0}')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}):$(echo ${ipath})/Scripts:$PATH
	python_version=$(python --version)
	fail_exit $? "$_PYTHON_HINT"

	KEY='HKLM\SOFTWARE\Node.js'
	entry=$(reg query ${KEY} //v InstallPath | awk '{ if($2=="REG_SZ") print $0}')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}):$PATH
	nodejs_version=$(node --version)
	fail_exit $? "$_NODEJS_HINT"
	
	npm_path=$(npm config get prefix)
	ipath=$(cygpath -u $npm_path)
	PATH=$PATH:$(echo ${ipath})
	

	KEY='HKLM\SOFTWARE\GitForWindows'
	entry=$(reg query ${KEY} //v InstallPath | awk '{ if($2=="REG_SZ") print $0 }')
	I=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	
	PATH=$PATH:$(echo ${I}/mingw64/bin:${I}/local/bin:${I}/usr/bin:${I}/bin)
	git_version=$(git --version)
	fail_exit $? "${_GIT_HINT}"
	
	KEY='HKLM\SOFTWARE\Kitware\CMake'
	entry=$(reg query ${KEY} //v InstallDir | awk '{ if($2=="REG_SZ") print $0 }')
	ipath=$(cygpath -u $( echo ${entry#*REG_SZ} | sed 's/^[ \t]*//g' ))
	PATH=$(echo ${ipath}/bin):$PATH
	#PATH=/c/Perl64/bin/:$PATH
	
	cmake_version=$(cmake --version)
	fail_exit $? "${_CMAKE_HINT}"	
	
	#install pkg config
	pkg-config --version
	if [ $? -ne 0 ] ; then
	    pacman -S pkg-config --noconfirm
		fail_exit $? "Install pkg-config failed."
	fi

	#nosetests
	nosetests --version
	if [ $? -ne 0 ] ; then
	   pip install nose
	   fail_exit $? "Install pkg-config failed."	   
	fi

	#install pkg config
	apidoc -h
	if [ $? -ne 0 ] ; then
	    npm install apidoc -g
		fail_exit $? "Install apidoc failed."
	fi
}


function msys2_opening(){
    type git        2>&1 &>/dev/null || return 1
	type cmake      2>&1 &>/dev/null || return 1
	type python     2>&1 &>/dev/null || return 1
	type pkg-config 2>&1 &>/dev/null || return 1
	type node       2>&1 &>/dev/null || return 1
	type apidoc     2>&1 &>/dev/null || return 1

	version=$(git --version | awk '{ print $3}')
	#echo "Git   $version" $(which git)
	echo " "
	echo " "
	echo " "
	echo -e "\033[1;37m\t\tGit        : $version \033[0m"
	#echo -e "\033[36m $(which git) \033[0m"
    version=$(echo $(cmake --version) | awk '{ print $3}')
	[ $? -ne 0 ] && return 1
	
	echo -e "\033[1;37m \t\tCMake      : $version \033[0m"
	
	version=$(node --version )
	echo -e "\033[1;37m \t\tNode.js    : ${version:1} \033[0m"

    version=$(apidoc -v  2>&1 | awk -F ':' '{ if( $2 ==" apidoc-generator version" ) print $3}')
	echo -e "\033[1;37m \t\tapidoc     : ${version:1} \033[0m"

    version=$(python --version  2>&1 | awk '{print $2}')
	[ $? -ne 0 ] && return 1
	echo -e "\033[1;37m \t\tPython     : $version \033[0m"

    version=$(nosetests --version  2>&1 | awk '{print $3}')
	echo -e "\033[1;37m \t\tnosetests  : $version \033[0m"
	
	version=$(pkg-config --version)
	echo -e "\033[1;37m \t\tpkg-config : $version \033[0m"
	
	echo -e "\033[7m
	Please make sure below info git repos (http://172.16.6.169:8080/) \033[0m \033[33m
	  git config --global user.email : $(git config --global user.email)
	  git config --global user.name  : $(git config --global user.name)	
	\033[0m"	
	
	_winsshd=$(cygpath -m $USERPROFILE)/.ssh
	_ssd=$(cygpath -m ~)/.ssh
	echo -e "
	\033[36m
	Copy key files,So that cerbero can fetch from git 	\033[0m
	\033[7m${_winsshd}\033[0m  => \033[7m${_ssd} (~/.ssh) \033[0m
	
	"
	return 0
}
if [ $MSYSTEM == msys ] ; then 
   if [ ! -f ./path.cache ] ; then
      msys2_load_path
	  echo $PATH > ./path.cache
   else
	  PATH=$(PATH=/usr/local/bin:/usr/bin:/bin && cat ./path.cache)
   fi
   reset   
   msys2_opening
   if [ $? -ne 0 ]; then
      rm -rf ./path.cache
	  fail_exit 1 "Maybe something changed, path.caced has deleled\n Please restar to reload enviroment"
   fi
fi
