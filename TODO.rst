* convert keystone population script into ansible module
* add per-service tags for selective service operations

* setup hostnames properly
* add /etc/hosts pre-population
* add nova_admin_tenant_id to /etc/neutron/neutron.conf
  this means that we can't use tenant_name, we have to figure out id... argh

* fix novncproxy_base_url in nova.conf
* implement centralized logging as per http://docs.openstack.org/openstack-ops/content/logging_monitoring.html

Done
====

...but not fully confirmed

+ reqiures::
 
     # yum install yum-plugin-priorities

  * if installed afterwards - needs to run::

     # yum distribution-synchronization

+ reqiuires ::

     # yum install openstack-selinux

+ add conditional to set up debug in config files

+ some odd issue with epel bootstrap
