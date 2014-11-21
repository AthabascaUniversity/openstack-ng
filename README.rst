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

Use
===

Setting up new platform
-----------------------

edit:
* hosts

  * neutron_bridge_* - settings for external-facing interface
  * instance_tunnels_interface_ip - Address of the interface that will handle VM-to-VM tunnelling

* group_vars/

  * all.yml
  * neutron.yml
  * nova.yml
  * glance.yml
  * keystone.yml

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


