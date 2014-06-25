#!/bin/sh

# This script is needed to add existing NIC to the OVS bridge
# and in case we were switching from using straight NIC interface
# we have to restart networking to pick up new settings

bridge_name=${1}
nic_name=${2}

ovs-vsctl --may-exist add-port $bridge_name $nic_name
service network restart
