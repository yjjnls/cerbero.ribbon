

_WD=$PWD

function version(){
    name=$1
	python -c "\
import sys;\
sys.path.append('packages');\
import custom;\
g=custom.$name();\
print g.version;\
	"
}
function build(){
    output=$1
	config=$2
	name=$(git config user.name)
	if [ "$name" == "" ]; then
	    git config user.name  cerbero.gstreamer
	fi
	email=$(git config user.email)
	if [ "$email" == "" ]; then
		git config user.email cerbero@gstreamer.freedesktop.org
	fi

	[ ! -d ${output} ] && mkdir -p ${output}
	echo -e "
	SDK:        gstreamer-1.0 
	Version:    $(version GStreamer)
	
	$(git config user.name)
	$(git config user.email)
	"
	exit 1

	./cerbero-uninstalled -c config/${config} bootstrap
    ./cerbero-uninstalled -c config/${config} package gstreamer-1.0 --tarball -o "${output}"
}


if [ "$OS" == "Windows_NT" ]; then
    outupd="SDKs/Windows/x86-64/gstreamer-1.0"
    build  "$output" "win64.cbc"
	if [  $? -ne 0 ] ; then
	    echo build Windows 64bits SDK failed
		exit 1
	fi

    outupd="SDKs/Windows/x86/gstreamer-1.0"
    build  "$output" "win32.cbc"
	if [  $? -ne 0 ] ; then
	    echo build Windows 32bits SDK failed
		exit 1
	fi

else
    outupd="SDKs/linux/x86/gstreamer-1.0/"
    build  "$output" "lin-x86-64.cbc"
	if [  $? -ne 0 ] ; then
	    echo build Linux 64bits SDK failed
		exit 1
	fi

fi
