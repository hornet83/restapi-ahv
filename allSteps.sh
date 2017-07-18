#!/bin/bash

if [[ $# -ne 1 ]]
then
  echo "usage: $0 vm-name"
  exit
fi

# Paul: we could change the detection of the location of the pyhton scripts by expecting 'allSteps.sh'
# to be on the PATH. This means that invoke as 'allSteps.sh vm-name' rather than './allSteps.sh vm-name'.
# Then use the following to auto-detect the location of the python scripts:
BIN=`which $0|awk 'BEGIN { FS="/" } { for ( i=2; i < NF; i++ ) { path = path "/" $i }; print path}'`

# set some vars
BIN="/usr/local/bin";
VM_NAME=$1;

# python scripts
CLONEVM="$BIN/clonevm_v2.py";
GETUUID="$BIN/getuuid_v2.py";
POWERSTATE="$BIN/powerstate_v2.py";
GETIPADDR="$BIN/getipaddr_v2.py";

# create the vm
python $CLONEVM centos-template $VM_NAME 1 1 1024;

# power on the vm
python $POWERSTATE $VM_NAME ON;

# get its IP address
IPADDR=$(python $GETIPADDR $VM_NAME vlan1);

echo $IPADDR;
