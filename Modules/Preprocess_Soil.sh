#!/bin/bash
## Processing HiHydrosoil
## Clip to study area
## Output files in wgs84
## Requirement: 7z installed
## Author: Sajid Pareeth, 2019


set -a
sttime=`date +%s`
source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('indir', help='Input directory with soil data')
parser.add_argument('ury', help='Upper right latitude (n)')
parser.add_argument('lly', help='Lower left latitude (s)')
parser.add_argument('llx', help='Lower left longitude (w)')
parser.add_argument('urx', help='Upper right longitude (e)')
EOF
echo required projdir: "$PROJDIR"
echo required indir: "$INDIR"
echo required ury: "$URY"
echo required lly: "$LLY"
echo required llx: "$LLX"
echo required urx: "$URX"

mkdir -p ${PROJDIR}/soil/.temp
TMP="${PROJDIR}/soil/.temp"

cd ${INDIR}
for i in `ls *.7z`; do 
	7z x ${i} -o${TMP}
done
cd ${TMP}
for i in `ls *.txt`; do 
	out=`echo $i|rev|cut -d. -f2-3|rev`
	gdal_translate -ot Float32 -projwin ${LLX} ${URY} ${URX} ${LLY} -a_srs epsg:4326 ${i} ${out}.tif
done
for i in `ls *gapfilled.tif`; do
	out=`echo $i|rev|cut -d. -f2-3|rev`
	gdal_calc.py -A ${i} --type=Float32 --outfile=${PROJDIR}/soil/${out}_wgs84.tif --cal="A/10000"
done

## CleanUp
rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED processing soil data at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "All outputs are in ${PROJDIR}/soil"
set +a
