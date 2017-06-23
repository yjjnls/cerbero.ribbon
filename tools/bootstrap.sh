__dir__=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
__cerberod__=$(cd ${__dir__}/.. && pwd)

#================================================#
#              CONFIGURATION                     #
#================================================#

VERSION=1.12.0
PATCHNO=1

CERBERO_REPO='http://172.16.66.94'
#HTTP_MIRROR='http://127.0.0.1:6786/mms/repo/mirror'

_MAP=(
   
   "cerbero-tarball@${CERBERO_REPO}/${VERSION}/cerbero-${VERSION}.tar.xz"
   "cerbero-tarball-sources-1@${CERBERO_REPO}/${VERSION}/cerbero-${VERSION}-sources-1.tar.xz"
     "cerbero-${VERSION}-build_tools-windows@${CERBERO_REPO}/${VERSION}/cerbero-${VERSION}-build_tools-windows.tar.xz"
   "cerbero-build_tools-linux-x86_64-${VERSION}@${CERBERO_REPO}/linux/x86_64/cerbero-build_tools-linux-x86_64-${VERSION}.tar.xz"
   "cerbero-tarball-sources-2@${CERBERO_REPO}/sources/cerbero-${VERSION}-sources-2.tar.xz"	
)

_GITIGNORE='*pyc
/build
/sources
/local
*.swp
cerbero.egg-info
/dist
'



#================================================#
#               FUNCTIONS                        #
#================================================#
function error(){
    echo -e "\033[0;31;1m $@ \033[0m"
	exit 1
}
function map(){
    key=$1
    for i in ${_MAP[*]}
	do
	    len=${#key}
		let len++
		if [ "${key}@" == ${i:0:$len} ]; then
		   echo ${i:$len}
		fi
	    
	done
}


function _download(){
    url=$1
	path=$2
	
	[ -z $path ] && path=$(basename $url)
	if [[ ${path:(-1)} == '.' || ${path:(-1)} == '/' ]] ; then
	    path="$(dirname $path)/$(basename $url)"
	fi
	echo $url "==>" $path
	if [ -f $path ] ; then
	   echo "$url already downloaded."
	   echo "   +-->$path"
	   return
	fi
	
	d=$(dirname $path)
	[ ! -d ${d} ] && mkdir -p ${d}
	
	wget -t 5 -w 10 $url  -O ${path}
	[ $? -ne 0 ] && error "Failed download: $mirror"

}

function _fetch(){
	url=$1
	path=$2
	
	if [ -n "$HTTP_MIRROR" ] ; then
	
		if [ "${url:0:7}" == "http://" ] ; then 
		   mirror="${HTTP_MIRROR}/${url:7}"
		   if [ -f $mirror ] ; then
		       cp -r $mirror $path
		   else
			   echo "fetch from mirror $path"
			   _download $mirror $path
		   fi
		   [ $? -eq 0 ] && return
		fi
	fi
	_download $url $path

}

function _tar(){
   echo "extract $2"
   tar $@ --checkpoint-action=dot --totals 
   [ $? -ne 0 ] && error "Failed unpack ${tarball}"
}

function _prepare(){
	cd ${__cerberod__}
	tarball=cerbero-${VERSION}.tar.xz
	if [ ! -f ${tarball} ] ; then
	   _fetch $(eval map 'cerbero-tarball')
	fi
	[ ! -d ~tmp ] && mkdir ~tmp
	_tar -xJf  ${tarball} -C ~tmp/. --checkpoint=1000
	mv ~tmp/cerbero-${VERSION}/sources .
	
	_fetch $(eval map 'cerbero-tarball-sources-1')
	_tar -xJf  cerbero-${VERSION}-sources-${PATCHNO}.tar.xz -C . --checkpoint=100
}

function _windows(){
      echo "start bootstraping for windows..."

   	_fetch $(eval map 'cerbero-${VERSION}-build_tools-windows')
	
	_tar -xJf cerbero-${VERSION}-build_tools-windows.tar.xz -C ./sources/. --checkpoint=100
	mkdir -p $cerberod/build/build_tools/bin
	
	#bootstrap
	./cerbero-uninstalled -c config/win64.cbc bootstrap &&
	./cerbero-uninstalled -c config/win32.cbc bootstrap

}
#-------------------------------------------------------------------------------------------------------------------------------------
function _gnu_linux(){
      echo "start bootstraping for GNU/Linux..."

      [ ! -d ./build/build-tools ] && mkdir -p ./build/build-tools

      _fetch $(eval map 'cerbero-build_tools-linux-$(uname -m)-${VERSION}')
      _tar -xJf cerbero-build_tools-linux-$(uname -m)-${VERSION}.tar.xz -C ./build/build-tools --checkpoint=100

      [ $(uname -m) = "x86_64" ] && ./cerbero-uninstalled bootstrap

      #_fetch $(eval map 'cerbero-tarball-sources-2')
      #_tar -xJf cerbero-${VERSION}-sources-2.tar.xz -C ./sources/. --checkpoint=100
}
#-------------------------------------------------------------------------------------------------------------------------------------
#_prepare

[ -n "$MSYSTEM" ] && _windows
[ $(uname -o) = "GNU/Linux" ] && _gnu_linux

