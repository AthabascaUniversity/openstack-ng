#!/bin/sh
NO=""
if [ $# -gt 0 ]
then
 case $1 in
  [nN][oO] )
    NO="no-" 
    ;;
 esac
fi
echo git update-index --${NO}assume-unchanged group_vars/all.yml group_vars/cinder.yml group_vars/glance.yml group_vars/keystone.yml group_vars/neutron.yml group_vars/nova.yml
