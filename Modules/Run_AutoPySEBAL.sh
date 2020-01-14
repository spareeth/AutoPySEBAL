#!/bin/bash
## Setting the variables for SEBAL
## Dates are stored in ${PROJDIR}/dates_L7.txt or ${PROJDIR}/dates_L8.txt
## Author: Sajid Pareeth, 2019

set -a
sttime=`date +%s`
source $(dirname $0)/argparse
argparse "$@" <<EOF || exit 1
parser.add_argument('projdir', help='Master project directory')
parser.add_argument('sensor', help='Landsat sensor, either one of the following - LC08;LE07;LT05;LT04')
parser.add_argument('lsdir', help='Input directory with all the landsat data')
parser.add_argument('meteo_db', help='gldas/era5, currently only gldas is supported')
parser.add_argument('start', help='start date (eg: yyyy-mm-dd)')
parser.add_argument('stop', help='stop date (eg: yyyy-mm-dd)')
parser.add_argument('res', help='desired resolution 15/30 m ')
EOF
echo required projdir: "$PROJDIR"
echo required sensor: "$SENSOR"
echo required lsdir: "$LSDIR"
echo required meteo_db: "$METEO_DB"
echo required start: "$START"
echo required stop: "$STOP"
echo required res: "$RES"
######
STYR=`echo ${START} | cut -d- -f1`
SPYR=`echo ${STOP} | cut -d- -f1`
STMM=`echo ${START} | cut -d- -f2`
SPMM=`echo ${STOP} | cut -d- -f2`
STDD=`echo ${START} | cut -d- -f3`
SPDD=`echo ${STOP} | cut -d- -f3`
STDOY=`date2doy ${START}`
SPDOY=`date2doy ${STOP}`
###############
nr=`echo ${SENSOR}|cut -c4`
mkdir -p ${PROJDIR}/landsat/${SENSOR}/temp
TMP="${PROJDIR}/landsat/${SENSOR}/temp"
out="${PROJDIR}/sebal_out/${RES}m"
mkdir -p ${out}
cd ${LSDIR}/${SENSOR}/${RES}m

### Prepare text files with require dates ###
ls -d ${SENSOR}*T1|cut -d_ -f4|sort -u > ${TMP}/dates_all.txt
dateutils.dseq -i %Y%m%d -f %Y%m%d ${SPYR}${SPMM}${SPDD} -1 ${STYR}${STMM}${STDD}|sort -u > ${TMP}/dates_seq.txt
comm -12  ${TMP}/dates_all.txt ${TMP}/dates_seq.txt > ${TMP}/dates.txt


for dt in `cat ${TMP}/dates.txt`; do
	FOLD=`ls *${dt}* -d`
	indir="${LSDIR}/${SENSOR}/${RES}m/${FOLD}"
	outdir="${out}/${FOLD}"
	itype=1
	pathdem="${PROJDIR}/elev/srtm_30m.tif"
	lsprefix="${FOLD}"
	lsnr=${nr}
	lsthermal=2
	hot=0
	cold=0
# METEO
	tinst="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Tair_inst_interp.tif"
	t24="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Tair_24_interp.tif"
	rhinst="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Rh_inst_interp.tif"
	rh24="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Rh_24_interp.tif"
	winst="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Wind_inst_interp.tif"
	w24="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_Wind_24_interp.tif"
	zx=2
	rad_method24=1
	rs24="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_SWdown_24_interp.tif"
	transm24=0.7
	rad_method_inst=1
	rsinst="${PROJDIR}/meteo/${METEO_DB}/GLDAS_NOAH025_3H_A${dt}_SWdown_inst_interp.tif"
	transminst=0.75
	obst_ht=0.4
# SOIL
	theta_sat_top="${PROJDIR}/soil/wcsat_topsoil_gapfilled_wgs84.tif"
	theta_sat_sub="${PROJDIR}/soil/wcsat_subsoil_gapfilled_wgs84.tif"
	theta_res_top="${PROJDIR}/soil/wcres_topsoil_gapfilled_wgs84.tif"
	theta_res_sub="${PROJDIR}/soil/wcres_subsoil_gapfilled_wgs84.tif"
	wilt_pt="${PROJDIR}/soil/wcpf4.2_topsoil_gapfilled_wgs84.tif"
	depl_factor=0.5
	field_capacity="${PROJDIR}/soil/wcpf2_topsoil_gapfilled_wgs84.tif"
	luemax=2.5
# Calib
	tcoldminin1=2  # low percentile ts_dem
	tcoldmaxin1=5  # high percentile ts_dem
	ndvihot_low1=1 # low percentile above zero
	ndvihot_high1=5 # high percentile above zero
	temp_lapse=0.0068 # r.regression.line mapx=srtm mapy=Temp_2018_07_05, get gain(b)
	res=${RES}

### COMMAND ####
	python ${HOME}/usr/local/bin/AutoSEBAL_v0.py ${indir} ${outdir} ${itype} ${pathdem} ${lsprefix} \
	${lsnr} ${lsthermal} ${hot} ${cold} ${tinst} ${t24} ${rhinst} ${rh24} ${winst} ${w24} ${zx} ${rad_method24} \
	${rs24} ${transm24} ${rad_method_inst} ${rsinst} ${transminst} ${obst_ht} ${theta_sat_top} ${theta_sat_sub} ${theta_res_top} ${theta_res_sub} ${wilt_pt} ${depl_factor} \
	${field_capacity} ${luemax} ${tcoldminin1} ${tcoldmaxin1} ${ndvihot_low1} ${ndvihot_high1} ${temp_lapse} ${res}
done

rm -rf ${TMP}
entime=`date +%s`
runtime=$((entime-sttime))
time=`date`
echo "FINISHED SEBAL processing at ${time}"
echo "Total time elapsed: ${runtime} s"
echo "All outputs are in ${PROJDIR}/sebal_out/${RES}m"
set +a
