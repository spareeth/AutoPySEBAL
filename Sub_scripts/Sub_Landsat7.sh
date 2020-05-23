#!/bin/bash
## This script prepares input data for PySEBAL
## Sajid Pareeth 2019

## GENERAL ##
if [ -z "$GISBASE" ] ; then
    echo "You must be in GRASS GIS to run this program." >&2
    exit 1
fi
export GRASS_OVERWRITE=1
export GRASS_MESSAGE_FORMAT=plain  # percent output as 0..1..2..
# setting environment, so that awk works properly in all languages
unset LC_ALL
LC_NUMERIC=C
export LC_NUMERIC

## Converting the bbox in latlong to UTM
N=`m.proj -i coordinates=$URX,$URY sep=,|cut -d, -f2`
E=`m.proj -i coordinates=$URX,$URY sep=,|cut -d, -f1`
S=`m.proj -i coordinates=$LLX,$LLY sep=,|cut -d, -f2`
W=`m.proj -i coordinates=$LLX,$LLY sep=,|cut -d, -f1`
######
## PROCESSING ##
cd ${PROJDIR}/landsat_raw/${SENSOR}
ls -d ${SENSOR}*T1|cut -d_ -f4|sort -u > ${TMP}/dates_all.txt
dateutils.dseq -i %Y%m%d -f %Y%m%d ${SPYR}${SPMM}${SPDD} -1 ${STYR}${STMM}${STDD}|sort -u > ${TMP}/dates_seq.txt
comm -12  ${TMP}/dates_all.txt ${TMP}/dates_seq.txt > ${TMP}/dates.txt
#cp ${TMP}/dates.txt ${PROJDIR}/dates_${SENSOR}.txt
SEN=${SENSOR}
for t in `cat ${TMP}/dates.txt`; do
	rm -f ${TMP}/names.txt
	sh -c "/bin/ls -d ${SENSOR}*${t}_*/" > ${TMP}/names.txt
	for j in `cat ${TMP}/names.txt`; do
		cd ${PROJDIR}/landsat_raw/${SENSOR}/${j}
		r.mask -r
		SCN=`ls *BQA.TIF|cut -d_ -f1-7`
		PRN=`ls *BQA.TIF|cut -d_ -f3`
		PTH=`echo ${PRN}|cut -c1-3`
		cp ${SCN}_MTL.txt ${TMP}/${SCN}_MTL.txt
		r.import in=${SCN}_BQA.TIF out=${SCN}_BQA memory=2000
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} -a
		r.mapcalc "${SCN}_BQA = if(${SCN}_BQA == 1,null(),${SCN}_BQA)"
		i.landsat8.qc cloud="Maybe,Yes" cloud_shadow="Yes" cirrus="Yes" output=${TMP}/cloud_rules.txt --o
		i.landsat8.qc snow_ice="Yes" snow_ice="Yes" output=${TMP}/snow_rules.txt
		r.reclass input=${SCN}_BQA output=${SCN}_cloud_Mask rules=${TMP}/cloud_rules.txt
		r.reclass input=${SCN}_BQA output=${SCN}_snow_Mask rules=${TMP}/snow_rules.txt
		r.import in=${SCN}_B8.TIF out=${SCN}_B8 memory=2000 resolution=region
		r.mapcalc "${SCN}_B8 = if(${SCN}_B8 == 0,null(),${SCN}_B8)" --o
		r.import in=${SCN}_B6_VCID_1.TIF out=${SCN}_B6_VCID_1 memory=2000 resolution=region
		r.mapcalc "${SCN}_B6_VCID_1 = if(${SCN}_B6_VCID_1 == 0,null(),${SCN}_B6_VCID_1)" --o
		r.import in=${SCN}_B6_VCID_2.TIF out=${SCN}_B6_VCID_2 memory=2000 resolution=region
		r.mapcalc "${SCN}_B6_VCID_2 = if(${SCN}_B6_VCID_2 == 0,null(),${SCN}_B6_VCID_2)" --o
		if [ ${RES} -eq 30 ]; then
			mkdir -p ${OUTDIR}/${RES}m
			OUTDIR1="${OUTDIR}/${RES}m"
			for i in 1 2 3 4 5 7; do
				r.import in=${SCN}_B${i}.TIF out=${SCN}_B${i} memory=2000 resolution=region
				r.mapcalc "${SCN}_B${i} = if(${SCN}_B${i} == 0,null(),${SCN}_B${i})" --o
			done
		else
			mkdir -p ${OUTDIR}/${RES}m
			OUTDIR1="${OUTDIR}/${RES}m"
			g.extension extension=i.fusion.hpf
			g.region n=${N} s=${S} w=${W} e=${E} res=30 -a
			for i in 1 2 3 4 5 6 7 9; do
				r.import in=${SCN}_B${i}.TIF out=${SCN}_B${i} memory=2000 resolution=region
				r.mapcalc "${SCN}_B${i} = if(${SCN}_B${i} == 0,null(),${SCN}_B${i})" --o
			done
			g.region n=${N} s=${S} w=${W} e=${E} res=${RES} -a
			i.fusion.hpf -l -c pan=${SCN}_B8 msx=${SCN}_B1,${SCN}_B2,${SCN}_B3,${SCN}_B4,${SCN}_B5,${SCN}_B7 center=high modulation=max trim=0.0 --o
			for i in 1 2 3 4 5 7; do
				g.rename rast=${SCN}_B${i}.hpf,${SCN}_B${i}
				r.mapcalc "${SCN}_B${i} = if(${SCN}_B${i} == 0,null(),${SCN}_B${i})" --o
			done
		fi
		#r.composite red=${SCN}_B4 green=${SCN}_B3 blue=${SCN}_B2 output=${SCN}_comp
		for i in 1 2 3 4 5 6_VCID_1 6_VCID_2 7; do
			r.mask rast=${SCN}_cloud_Mask --o
			r.mapcalc "${SCN}_B${i} = ${SCN}_B${i}" --o
			r.mask rast=${SCN}_snow_Mask --o
			r.mapcalc "${SCN}_B${i} = ${SCN}_B${i}" --o
		done
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} -a
	done
	r.mask -r
	DIR="${SEN}_p${PTH}_patch_${t}_T1"
	mkdir -p ${OUTDIR1}/${DIR}
	cp -rf ${TMP}/${SCN}_MTL.txt ${OUTDIR1}/${DIR}/${DIR}_MTL.txt
	## Now patching to bbox
	g.region n=${N} s=${S} w=${W} e=${E} res=${RES} -a
	MAPS1=`g.list rast pattern=*${t}*BQA sep=,`
	OUT1="${SEN}_p${PTH}_patch_${t}_T1_BQA"
	MAPS2=`g.list rast pattern=*${t}*cloud_Mask sep=,`
	OUT2="${SEN}_p${PTH}_patch_${t}_T1_cloud_Mask"
	MAPS3=`g.list rast pattern=*${t}*snow_Mask sep=,`
	OUT3="${SEN}_p${PTH}_patch_${t}_T1_snow_Mask"
	MAPCOUNT=`g.list rast pattern=*${t}*BQA | wc -l`
	if [ ${MAPCOUNT} -eq 0 ]; then
		echo "Not enough data to patch"
		continue
	elif [ ${MAPCOUNT} -eq 1 ]; then
		r.mapcalc "${OUT1} = ${MAPS1}"
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT1} -a
		r.out.gdal in=${OUT1} out=${OUTDIR1}/${DIR}/${OUT1}.TIF nodata=0 --o -f
		r.mapcalc "${OUT2} = ${MAPS2}"
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT2} -a
		r.out.gdal in=${OUT2} out=${OUTDIR1}/${DIR}/${OUT2}.TIF nodata=0 --o -f
		r.mapcalc "${OUT3} = ${MAPS3}"
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT3} -a
		r.out.gdal in=${OUT3} out=${OUTDIR1}/${DIR}/${OUT3}.TIF nodata=0 --o -f
	else
		r.patch input=${MAPS1} output=${OUT1}
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT1} -a
		r.out.gdal in=${OUT1} out=${OUTDIR1}/${DIR}/${OUT1}.TIF nodata=0 --o -f
		r.patch input=${MAPS2} output=${OUT2}
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT2} -a
		r.out.gdal in=${OUT2} out=${OUTDIR1}/${DIR}/${OUT2}.TIF nodata=0 --o -f
		r.patch input=${MAPS3} output=${OUT3}
		g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT3} -a
		r.out.gdal in=${OUT3} out=${OUTDIR1}/${DIR}/${OUT3}.TIF nodata=0 --o -f
	fi
	for i in 1 2 3 4 5 6_VCID_1 6_VCID_2 7; do
		MAPS=`g.list rast pattern=*${t}*B${i} sep=,`
		MAPCOUNT1=`g.list rast pattern=*${t}*B${i} | wc -l`
		OUT="${SEN}_p${PTH}_patch_${t}_T1_B${i}"
		if [ ${MAPCOUNT1} -eq 0 ]; then
			echo "Not enough data to patch"
			continue
		elif [ ${MAPCOUNT1} -eq 1 ]; then
			r.mapcalc "${OUT} = ${MAPS}"
			g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT} -a
			r.out.gdal in=${OUT} out=${OUTDIR1}/${DIR}/${OUT}.TIF nodata=0 --o -f
		else
			r.patch input=${MAPS} output=${OUT}
			g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${OUT} -a
			r.out.gdal in=${OUT} out=${OUTDIR1}/${DIR}/${OUT}.TIF nodata=0 --o -f
		fi
	done
	g.region n=${N} s=${S} w=${W} e=${E} res=${RES} zoom=${SEN}_p${PTH}_patch_${t}_T1_B4 -a
	i.colors.enhance red=${SEN}_p${PTH}_patch_${t}_T1_B4 green=${SEN}_p${PTH}_patch_${t}_T1_B3 blue=${SEN}_p${PTH}_patch_${t}_T1_B2 strength=95
	r.composite red=${SEN}_p${PTH}_patch_${t}_T1_B4 green=${SEN}_p${PTH}_patch_${t}_T1_B3 blue=${SEN}_p${PTH}_patch_${t}_T1_B2 output=${SEN}_p${PTH}_patch_${t}_T1_comp
	r.out.gdal in=${SEN}_p${PTH}_patch_${t}_T1_comp out=${OUTDIR1}/${DIR}/${SEN}_p${PTH}_patch_${t}_T1_comp.TIF nodata=0 --o -f
	g.remove type=rast pattern=LC08* exclude="*patch*" -f
	g.remove type=rast pattern=LC08* exclude="*patch*" -f
	g.remove type=rast pattern=LE07* exclude="*patch*" -f
	g.remove type=rast pattern=LE07* exclude="*patch*" -f
	cd ${PROJDIR}/landsat_raw/${SENSOR}
	g.region n=${N} s=${S} w=${W} e=${E} res=${RES} -a
done
#cd ${PROJDIR}/landsat/${SENSOR}
#ls -d ${SENSOR}*T1 > ${PROJDIR}/${SENSOR}_folders.txt
