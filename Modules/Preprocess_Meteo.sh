#!/bin/bash
## Processing GLDAS
## Clip and interpolate 
## Output files in wgs84
## Author: Sajid Pareeth, 2019

set -a
sttime=`date +%s`
source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('db', help='gldas/era5, currently only gldas is supported')
parser.add_argument('indir', help='Input directory with meteo raster data')
parser.add_argument('ury', help='Upper right latitude (n)')
parser.add_argument('lly', help='Lower left latitude (s)')
parser.add_argument('llx', help='Lower left longitude (w)')
parser.add_argument('urx', help='Upper right longitude (e)')
parser.add_argument('grassdb', help='Path to grass data base (eg: /home/grassdata)')
parser.add_argument('start', help='start date (eg: yyyy-mm-dd)')
parser.add_argument('stop', help='stop date (eg: yyyy-mm-dd)')
EOF
echo required projdir: "$PROJDIR"
echo required db: "$DB"
echo required indir: "$INDIR"
echo required ury: "$URY"
echo required lly: "$LLY"
echo required llx: "$LLX"
echo required urx: "$URX"
echo required grassdb: "$GRASSDB"
echo required start: "$START"
echo required grassdb: "$STOP"

# mkdir -p ${PROJDIR}/meteo/${DB}
mkdir -p ${PROJDIR}/meteo/${DB}/.temp
TMP="${PROJDIR}/meteo/${DB}/.temp"
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
grass7_trunk -c epsg:4326 ${GRASSDB}/latlong_temp -e --text
# now we can use this new location and run the job defined via	GRASS_BATCH_JOB

LN=`which Preprocess_Meteo`
LNK=`readlink ${LN}`
OLN=`echo ${LNK}|rev|cut -d/ -f3- |rev`
OLNK="${OLN}/Sub_scripts"

export GRASS_BATCH_JOB="${OLNK}/Sub_Meteo.sh"
grass7_trunk -c ${GRASSDB}/latlong_temp/meteo --text
unset GRASS_BATCH_JOB

## CleanUp
rm -rf ${GRASSDB}/latlong_temp
rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED processing meteo data at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "All outputs are in ${PROJDIR}/meteo/${DB}"
set +a
