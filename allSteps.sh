#!/bin/bash

# set some vars
BIN="/usr/local/bin";
VM_NAME="demovm1";

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
