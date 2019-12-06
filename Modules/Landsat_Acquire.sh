#!/bin/bash
## Author: Sajid Pareeth, 2017
## Automating the Landsat data acquisition
## Downloading Landsat (4/5/7/8) data from Google cloud
## Google storage: gs://gcp-public-data-landsat/
## Pre-requisite: gsutil must be installed and accessible

sttime=`date +%s`
exitprocedure()
{
 g.message -e 'User break!'
 rm -rf ${TMP}
 #rm -rf ${OUTDIR}/*
 exit 1
}
# shell check for user break (signal list: trap -l)
trap "exitprocedure" 2 3 15

source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('pr', help='L8 paths/rows to download (eg: 147039,147040)')
parser.add_argument('sensor', help='Landsat sensor, either one of the following - LC08;LE07;LT05;LT04')
parser.add_argument('start', help='start date (eg: yyyy-mm)')
parser.add_argument('stop', help='stop date (eg: yyyy-mm)')
parser.add_argument('-l', '--list', help='optional, just list the landsat data, not download')
EOF
echo required projdir: "$PROJDIR"
echo required pr: "$PR"
echo required sensor: "$SENSOR"
echo required start: "$START"
echo required stop: "$STOP"
echo required stop: "$LIST"

mkdir -p ${PROJDIR}/landsat_raw/${SENSOR}
TMP="${PROJDIR}/landsat_raw/${SENSOR}/temp"

STYR=`echo ${START} | cut -d- -f1`
SPYR=`echo ${STOP} | cut -d- -f1`
STMM=`echo ${START} | cut -d- -f2`
SPMM=`echo ${STOP} | cut -d- -f2`

PRN=`echo ${PR}|sed 's/,/ /g'`

for T in ${PRN}; do
	P=`echo ${T}|cut -c1-3`
	R=`echo ${T}|cut -c4-6`
	for yy in `seq ${STYR} ${SPYR}`; do
		if [ ${yy} -eq ${STYR} ] && [ ${yy} -ne ${SPYR} ]; then
			sd=${STMM}
			nd=12
		elif [ ${yy} -eq ${SPYR} ] && [ ${yy} -ne ${STYR} ]; then
			sd=1
			nd=${SPMM}
		elif [ ${yy} -eq ${STYR} ] && [ ${yy} -eq ${SPYR} ]; then
			sd=${STMM}
			nd=${SPMM}
		else
			sd=1
			nd=12
		fi
		for i in `seq ${sd} ${nd}`; do
			mm=`echo $i | awk '{ printf("%02d\n", $1) }'`
			if [[ ! -z ${LIST} ]]; then
				gsutil ls -d gs://gcp-public-data-landsat/${SENSOR}/01/${P}/${R}/${SENSOR}_*_${PRN}_${yy}${mm}*_*_01_T1
			else
				gsutil -m cp -r gs://gcp-public-data-landsat/${SENSOR}/01/${P}/${R}/${SENSOR}_*_${PRN}_${yy}${mm}*T1 ${PROJDIR}/landsat_raw/${SENSOR}
			fi
		done
	done
done
## CleanUp
rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED downloading landsat data at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "Check ${OUTDIR}"
