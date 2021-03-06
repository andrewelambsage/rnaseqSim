#!/bin/bash

# Usage Example:
# $ ./deploy.sh simTest 5 5 syn7993100 syn8043478


SIM_NAME=$1 # Name of sim data
NUM_EVENTS=$2 # Number of fusion events to simulate
DEPTH=$3 # Target depth
EXPRESION_PROFILE=$4 # synapse id for expression profile
RSEM_MODEL=$5 # synapse id for RSEM model

MACHINE_TYPE=n1-standard-8
DISK_SIZE=300
TIMEOUT=126000 #35 hours in seconds
SNAPSHOT=sim-fusion-base
ZONE=us-west1-b
PROJECT=isb-cgc-04-0029

gcloud compute disks create sim-fusion-disk-$SIM_NAME \
--source-snapshot $SNAPSHOT --size $DISK_SIZE --project $PROJECT --zone $ZONE

gcloud compute instances create sim-fusion-$SIM_NAME \
--disk name=sim-fusion-disk-$SIM_NAME,auto-delete=yes,boot=yes \
--scopes storage-rw --machine-type $MACHINE_TYPE --project $PROJECT --zone $ZONE

sleep 60

gcloud compute --project $PROJECT ssh sim-fusion-$SIM_NAME --zone $ZONE "nohup sudo sudo -i -u ubuntu bash /home/ubuntu/rnaseqSim/run_workflow.sh $SIM_NAME $NUM_EVENTS $DEPTH $EXPRESION_PROFILE $RSEM_MODEL $TIMEOUT > /tmp/eval.out 2> /tmp/eval.err &"
