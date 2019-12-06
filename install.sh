#!/bin/sh
## Author: Sajid Pareeth, 2017
## This script creates a sym link of all the Cropsat modules in /usr/local/bin (Assuming /usr/local/bin is in PATH)
## This is the installation step, once all the requirements are met

sudo chmod +x Modules/*.sh
sudo chmod +x Aux_scripts/*.sh
sudo chmod +x Sub_scripts/*.sh
IN=`pwd`
## Creating symbolic links of all the scripts in Modules and Aux_scripts folder

for i in `ls Modules/*.sh`; do
	MOD=`echo $i|cut -d/ -f2|cut -d. -f1`
	sudo ln -sf ${IN}/${i} /usr/local/bin/${MOD}
done

for i in `ls Aux_scripts/*`; do
	MOD=`echo $i|cut -d/ -f2|cut -d. -f1`
	sudo ln -sf ${IN}/${i} /usr/local/bin/${MOD}
done

mkdir -p ${HOME}/.aws
cp Others/aws_config ${HOME}/.aws/config
cp Others/aws_credentials ${HOME}/.aws/credentials

echo "Successfully installed the modules"
echo "Please remember to create symlink to otbenv.profile in /usr/local/bin if OTB is installed using Linux binary"
exit 0
