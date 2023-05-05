#!/bin/sh

NFS_DIR=~/nfs4
IP_ADDR=192.168.10.117

[ -n "$1" ] && {
	IP_ADDR=$1
}

mkdir -p ${NFS_DIR}

mount -v -t nfs ${IP_ADDR}:/home/ken/nfs4 ${NFS_DIR} -o nfsvers=4 -o nolock
