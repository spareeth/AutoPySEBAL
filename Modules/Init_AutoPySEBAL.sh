#!/bin/bash
## Script to prepare for further processing
## Create input folders, report general stuff related to project
## Author: Sajid Pareeth, 2019

source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='project directory')
EOF
echo required projdir: "$PROJDIR"

mkdir -p ${PROJDIR}/meteo ${PROJDIR}/soil ${PROJDIR}/elev ${PROJDIR}/landsat_raw ${PROJDIR}/landsat ${PROJDIR}/sebal_out

TIME=`date`
echo "FINISHED processing at ${TIME}"
echo "Created folders input folders for meteo, soil, elev, landsat and sebal_out"
echo "Now run pre processing modules"

