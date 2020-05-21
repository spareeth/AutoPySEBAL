#!/bin/bash
## Pre-processing Landsat data
## Patch, cloud mask, clip landsat data 
## Output files in UTM
## Author: Sajid Pareeth, 2019

set -a
sttime=`date +%s`
source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('sensor', help='Landsat sensor, either one of the following - LC08;LE07;LT05;LT04')
parser.add_argument('llx', help='Lower left longitude (w)')
parser.add_argument('lly', help='Lower left latitude (s)')
parser.add_argument('urx', help='Upper right longitude (e)')
parser.add_argument('ury', help='Upper right latitude (n)')
parser.add_argument('crs', help='UTM zone of L8 tiles in EPSG code eg: epsg:32632')
parser.add_argument('res', help='desired resolution 15/30 m ')
parser.add_argument('grassdb', help='Path to grass data base (eg: /home/grassdata)')
parser.add_argument('start', help='start date (eg: yyyy-mm-dd)')
parser.add_argument('stop', help='stop date (eg: yyyy-mm-dd)')
EOF
echo required projdir: "$PROJDIR"
echo required sensor: "$SENSOR"
echo required llx: "$LLX"
echo required lly: "$LLY"
echo required urx: "$URX"
echo required ury: "$URY"
echo required crs: "$CRS"
echo required grassdb: "$RES"
echo required grassdb: "$GRASSDB"
echo required start: "$START"
echo required grassdb: "$STOP"

mkdir -p ${PROJDIR}/landsat/${SENSOR}/temp
TMP="${PROJDIR}/landsat/${SENSOR}/temp"
OUTDIR="${PROJDIR}/landsat/${SENSOR}"
######
STYR=`echo ${START} | cut -d- -f1`
SPYR=`echo ${STOP} | cut -d- -f1`
STMM=`echo ${START} | cut -d- -f2`
SPMM=`echo ${STOP} | cut -d- -f2`
STDD=`echo ${START} | cut -d- -f3`
SPDD=`echo ${STOP} | cut -d- -f3`
STDOY=`date2doy ${START}`
SPDOY=`date2doy ${STOP}`

# create new temporary location for the job, exit after creation of this location
grass78 -c ${CRS} ${GRASSDB}/utm_temp -e --text
# now we can use this new location and run the job defined via	GRASS_BATCH_JOB

LN=`which Preprocess_Landsat`
LNK=`readlink ${LN}`
OLN=`echo ${LNK}|rev|cut -d/ -f3- |rev`
OLNK="${OLN}/Sub_scripts"
L8="LC08"
L7="LE07"

if [ ${SENSOR} == ${L8} ]; then
	export GRASS_BATCH_JOB="${OLNK}/Sub_Landsat8.sh"
	grass78 -c ${GRASSDB}/utm_temp/landsat8 --text
	unset GRASS_BATCH_JOB
else
	export GRASS_BATCH_JOB="${OLNK}/Sub_Landsat7.sh"
	grass78 -c ${GRASSDB}/utm_temp/landsat7 --text
	unset GRASS_BATCH_JOB
fi
## CleanUp
rm -rf ${GRASSDB}/utm_temp
rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED pre-processing landsat data at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "All outputs are in ${PROJDIR}/landsat/${SENSOR}/${RES}m"
set +a
