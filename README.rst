openstack-ng
============

Ansible playbook for setting up OpenStack infrastructure from scratch. Aims to replace openstack-setup and ansible-redhat-openstack

Assumptions
===========

1. Platform: RedHat
2. Distribution: RDO
3. Using OpenVSwitch & Neutron

Architecture
============

`Original blueprint <http://docs.openstack.org/icehouse/install-guide/install/yum/content/ch_overview.html>`_ 

.. image:: http://docs.openstack.org/icehouse/install-guide/install/yum/content/figures/1/figures/installguide_arch-neutron.png
   :alt: Original architecture for the deployment

Supported deployment model allows for multi-node deployment where practically every service lives on it's own node.

Known bugs
==========

EPEL bootstrap fails for some reason. CLI invocation for update or manual setup of EPEL helps to get around this problem. Will need to fix EPEL bootstraping.

Use
===

Setting up new platform
-----------------------

edit:

* hosts

  * neutron_bridge_* - settings for external-facing interface on Neutron-Network node

    * "bad things will happen" when combining this and management interface - bridge config script will likely hang or kill the interface

  * instance_tunnels_interface_ip - Address of the interface that will handle VM-to-VM tunnelling, also required on Neutron-Network node

    * when doing single-node deployment - it could be some loopback device

  * quite a few group variables defined per-inventory to simplify management of several instances and avoid clashes in group_vars

* group_vars/

  * all.yml

    * virtual_deploy - when deploying into VMs - set that to True

  * neutron.yml
  * nova.yml
  * glance.yml
  * keystone.yml
  * cinder.yml

Run::

  $ ansible-playbook -i hosts site.yml

Stop/start openstack services
-----------------------------

Stop::

  $ ansible-playbook -i hosts -t service_stop site.yml

Start::

  $ ansible-playbook -i hosts -t service_stop site.yml

Useful tags
-----------

service_start
+++++++++++++

start the services required

service_stop
++++++++++++

stop all OpenStack services (it does not shut down supporting services like messagebus, libvirt etc.)

service_restart
+++++++++++++++

this tag has limited coverage and will restart some subset of OpenStack services but not all... best to use combination of "service_stop" followed by "service_start"

configure
+++++++++

deploy configuration files. Most likely you'll be using it with "service_stop" and "service_start"

initialize
++++++++++

this could be somewhat destructive as it typically wipes the data and re-initializes databases etc. some aspects are controlled by \*_force_init variables

install
+++++++

only install packages

repo_setup
++++++++++

setup all required repos
