
PKGS=(
base-libs
base-system-1.0
base-crypto
gstreamer-1.0
gstreamer-1.0-capture
gstreamer-1.0-codecs
gstreamer-1.0-codecs-gpl
gstreamer-1.0-codecs-restricted
gstreamer-1.0-core
gstreamer-1.0-devtools
gstreamer-1.0-dvd
gstreamer-1.0-editing
gstreamer-1.0-effects
gstreamer-1.0-encoding
gstreamer-1.0-libav
gstreamer-1.0-net
gstreamer-1.0-net-restricted
gstreamer-1.0-playback
gstreamer-1.0-system
gstreamer-1.0-visualizers
gstreamer-1.0-vs-templates
vsintegration-1.0
)

function _windows(){
    echo "start bundle for windows..."

    for arch in win64 win32
    do
        for pkg in ${PKGS[*]}
        do
            echo $pkg
            ./cerbero-uninstalled -c config/$arch.cbc package ${pkg} --tarball
        done
    done
}



function _gnu_linux(){
    echo "start bundle for GNU/Linux..."

    #for libffi build
    [ $(awk '{match($0,/^ID=(.*)/,a);NF;print a[1]}' /etc/os-release|awk NF) = "ubuntu" ] && 
      git config --global user.email "daihongjun@kedacom.com" &&
      git config --global user.name "daihongjun"


    if [ $(uname -m) = "x86_64" ]; then
        for pkg in ${PKGS[*]}
        do
            [[ $pkg = "base-libs" || $pkg = "gstreamer-1.0-vs-templates" || $pkg = "vsintegration-1.0" ]] && continue
            echo $pkg
            ./cerbero-uninstalled -c config/lin-x86-64.cbc package ${pkg} --tarball
        done
    fi
}

[ -n "$MSYSTEM" ] && _windows
[ $(uname -o) = "GNU/Linux" ] && _gnu_linux
