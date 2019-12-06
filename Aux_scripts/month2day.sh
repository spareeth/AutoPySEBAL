#!/bin/sh

# Markus Neteler 2005
# $Date: 2005-08-17 10:36:39 +0200 (Wed, 17 Aug 2005) $

MONTHDAYS="31 28 31 30 31 30 31 31 30 31 30 31"

if [ "$1" = "-h" -o "$1" = "-help" -o "$1" = "--help" ] ; then
   echo ""
   echo "month2day.sh -l [startmonth stopmonth]"
   echo "-l: leap year"
   exit 1
fi

if [ $# -lt 1 ] ; then
    START=1
    STOP=12
else
  # >= 1 parm
        if [ "$1" = "-l" ] ; then
              MONTHDAYS="31 29 31 30 31 30 31 31 30 31 30 31"
        fi
        if [ "$1" != "-l" -a $# -ne 2 ] ; then
           echo "incorrect parameters"
           exit 1
        else
           if [ $# -eq 3 ] ; then
               START=$2
               STOP=$3
           else
              if [ $# -eq 2 ] ; then
                  START=$1
                  STOP=$2
              else
                  START=1
                  STOP=12
              fi
           fi
        fi
fi

# some initialization stuff
BEFORE=`expr $START - 1`
if [ $BEFORE -ge 1 ] ; then
  MONTHGONE="`echo $MONTHDAYS | cut -d' ' -f1-$BEFORE`"
else
  MONTHGONE=""
fi
DAYSGONE=`echo $MONTHGONE | tr -s ' ' '+' | bc`
REALMONTHDAYS="`echo $MONTHDAYS | cut -d' ' -f$START-$STOP`"

# loop
f=`expr $START - 1`
g=$DAYSGONE
for i in $REALMONTHDAYS ; do
  f=`expr $f + 1`
  for m in `seq 1 $i` ; do
   g=`expr $g + 1`
   echo "$f:$m:$g"
  done
done

