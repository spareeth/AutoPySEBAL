#!/bin/bash
## This script prepares input data for PySEBAL
## Given two sets of lat long defining the bbox in wgs84
## Sajid Pareeth 2019

## GENERAL ##
if [ -z "$GISBASE" ] ; then
    echo "You must be in GRASS GIS to run this program." >&2
    exit 1
fi
export GRASS_OVERWRITE=1
export GRASS_MESSAGE_FORMAT=plain
# percent output as 0..1..2..
# setting environment, so that awk works properly in all languages
unset LC_ALL
LC_NUMERIC=C
export LC_NUMERIC

## PROCESSING ##
g.region n=${URY} s=${LLY} w=${LLX} e=${URX} res=0:00:01 -a
g.extension extension=r.in.srtm.region
r.in.srtm.region -1 user="spareeth" password="jungle_123" output=srtm_30m memory=2000
r.out.gdal in=srtm_30m out=${PROJDIR}/elev/srtm_30m.tif
