#!/bin/sh
## Author: Sajid Pareeth, 2017
## This script creates a sym link of all the AutoPySEBAL modules in /usr/local/bin (Assuming /usr/local/bin is in PATH)
## This is the installation step, once all the requirements are met

chmod +x Modules/*.sh
chmod +x Aux_scripts/*.sh
chmod +x Sub_scripts/*.sh
IN=`pwd`
## Creating symbolic links of all the scripts in Modules and Aux_scripts folder

for i in `ls Modules/*.sh`; do
	MOD=`echo $i|cut -d/ -f2|cut -d. -f1`
	ln -sf ${IN}/${i} ${HOME}/usr/local/bin/${MOD}
done

for i in `ls Aux_scripts/*`; do
	MOD=`echo $i|cut -d/ -f2|cut -d. -f1`
	ln -sf ${IN}/${i} ${HOME}/usr/local/bin/${MOD}
done

echo "Successfully installed the modules"
exit 0
