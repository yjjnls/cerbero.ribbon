RECIPES={
boost
Theron
libevent
log4cplus
libuv
libwebsockets
protobuf
rapidjson
mysql-connector-c
rocksdb
sqlite3
boost
libusrsctp
#openwebrtc
#openwebrtc-gst-plugins
}

build(){
for recipe in ${RECIPES[*]}
do
    echo $recipe
   ./cerbero-uninstalled buildone ${recipe}
done
}
