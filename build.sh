

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
	config=$1
	
    git config --global user.name  Mingyi Zhang
	git config --global user.email mingyi.z@outlook.com

	[ ! -d ${output} ] && mkdir -p ${output}
	echo -e "
	SDK:        Ribbon
	Version:    $(version Ribbon)
	
	$(git config user.name)
	$(git config user.email)
	"
	output="SDK/ribbon/$(version Ribbon)"
	[ ! -d ${output} ] && mkdir -p $output
	
	if [ ! -f ${config}.bootstrap ] ; then
		./cerbero-uninstalled -c config/${config} bootstrap
		[ $? -eq 0 ] &&  touch ${config}.bootstrap
	fi
	if [ ! -f ${config}.built ] ; then
		./cerbero-uninstalled -c config/${config} package ribbon --tarball -a gz -o "${output}"
		[ $? -eq 0 ] &&  touch ${config}.built
	fi
}


if [ "$OS" == "Windows_NT" ]; then
    for conf in  win32d win32 win64d win64
	do
	    echo "    ====== build $conf ======="
		build ${conf}.cbc
		if [  $? -ne 0 ] ; then
			echo build $conf SDK failed
			exit 1
		fi
	done

else
	echo "    ====== build Linux x86_64 ======="
    build  linux-x86-64.cbc
	if [  $? -ne 0 ] ; then
	    echo build Linux 64bits SDK failed
		exit 1
	fi

fi
