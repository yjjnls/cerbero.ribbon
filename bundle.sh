
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

for arch in win64 win32
do
	for pkg in ${PKGS[*]}
	do
	     echo $pkg
	    echo ./cerbero-uninstalled -c config/$arch.cbc package ${pkg} --tarball
	done
done
