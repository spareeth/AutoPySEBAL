#!/bin/bash
## Processing SRTM for the studyarea
## Clip to study area
## Output files in wgs84
## Requirement: installed GRASS addon r.in.srtm.region
## Author: Sajid Pareeth, 2019


set -a
sttime=`date +%s`
source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('grassdb', help='Path to grass data base (eg: /home/grassdata)')
parser.add_argument('ury', help='Upper right latitude (n)')
parser.add_argument('lly', help='Lower left latitude (s)')
parser.add_argument('llx', help='Lower left longitude (w)')
parser.add_argument('urx', help='Upper right longitude (e)')
EOF
echo required projdir: "$PROJDIR"
echo required grassdb: "$GRASSDB"
echo required ury: "$URY"
echo required lly: "$LLY"
echo required llx: "$LLX"
echo required urx: "$URX"

mkdir -p ${PROJDIR}/elev/.temp
TMP="${PROJDIR}/elev/.temp"

# create new temporary location for the job, exit after creation of this location
grass7_latest -c epsg:4326 ${GRASSDB}/latlong_temp -e --text
# now we can use this new location and run the job defined via	GRASS_BATCH_JOB

LN=`which Preprocess_Elev`
LNK=`readlink ${LN}`
OLN=`echo ${LNK}|rev|cut -d/ -f3- |rev`
OLNK="${OLN}/Sub_scripts"

export GRASS_BATCH_JOB="${OLNK}/Sub_Elev.sh"
grass7_latest -c ${GRASSDB}/latlong_temp/elev --text
unset GRASS_BATCH_JOB

## CleanUp
rm -rf ${GRASSDB}/latlong_temp
rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED processing SRTM elevation at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "All outputs are in ${PROJDIR}/elev/"
set +a
