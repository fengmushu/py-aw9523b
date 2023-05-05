#!/bin/bash

LOOP_CNT=5
URL_bootstrap="http://117.48.195.14:1980/ken/ht160.txt"
HTP_USR='root'
HTP_PWD='webroot@tenbay'
LOG_runtime='runtime.log'

do_bootstrap()
{
	chmod a+x ./bootstrap.sh

	echo "do bootstrap ..." >> $LOG_runtime
	./bootstrap.sh >> $LOG_runtime 2>&1

	return 1
}

main()
{
	until [ ${LOOP_CNT} -le 0 ]; do
		wget -c --http-user=${HTP_USR} --http-password=${HTP_PWD} $URL_bootstrap -O bootstrap.sh -a $LOG_runtime || {
			sleep 1
			continue
		}

		do_bootstrap && return

		let LOOP_CNT=${LOOP_CNT}-1
	done
}

main